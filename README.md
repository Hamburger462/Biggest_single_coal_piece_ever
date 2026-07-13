# Biggest Single Coal Piece Ever (BSCPE)

BSCPE is a mineral identification tool: upload a photo of a mineral specimen (optionally with field notes like hardness, luster, or streak color), and get back a structured identification — a mineral name and chemical formula — along with a ranked list of alternative candidates when the top answer isn't a sure thing.

## Table of contents

- [Purpose and goal](#purpose-and-goal)
- [The model](#the-model)
- [Backend architecture](#backend-architecture-fastapi)
- [Frontend architecture](#frontend-architecture-react)
- [Project structure](#project-structure)
- [Known limitations](#known-limitations)
- [Getting started](#getting-started)

## Purpose and goal

Identifying a mineral from a photo alone is a fine-grained visual recognition problem — many minerals share color, shape, and luster, and telling them apart often depends on details a general-purpose vision model was never trained to notice. BSCPE's goal is to turn that open-ended guessing problem into a structured, specific answer by fine-tuning a vision-language model on a labeled set of mineral photographs, rather than relying on a general-purpose model's out-of-the-box (and, as it turns out, unreliable and fabrication-prone) attempt at mineral identification.

The project is split into three layers:

1. **A fine-tuned vision-language model** that does the actual identification.
2. **A FastAPI backend** that serves the model and persists identification history.
3. **A React frontend** where a person uploads a photo, gets a result, and can review past identifications.

## The model

**Base model:** [`llava-hf/llava-1.5-7b-hf`](https://huggingface.co/llava-hf/llava-1.5-7b-hf) — a 7-billion-parameter vision-language model (the Hugging Face Transformers port of LLaVA v1.5).

**Fine-tuning approach:** QLoRA — the base model is loaded 4-bit quantized (via `bitsandbytes`), and a LoRA adapter (via `peft`) is trained on top of it in `bf16`. Two details mattered a lot in practice:

- The LoRA adapter targets not just the language model's attention/MLP layers, but also the `multi_modal_projector` — the small module that maps visual features into the language model's embedding space. Leaving it frozen (the default for most LLaVA fine-tuning setups) meant the adapter could only change *how* the model phrased its answer, not how it connected image content to the answer in the first place — which showed up as a hard loss plateau early in training.
- A short learning-rate warmup and `bf16` compute (rather than `fp16`) were needed for stable QLoRA training.

**Dataset:** training data combines the [Mineral Photos dataset](https://www.kaggle.com/datasets/floriangeillon/mineral-photos) on Kaggle with programmatically generated text prompts. Each image is paired with:
- A naturally varied question — a plain "what is this?", a geological-log style description, or field-note style observations (hardness, luster, where it was found).
- A structured JSON answer: `{"mineral_name": "...", "chemical_formula": "..."}`.

The final training run used 15 mineral classes, balanced to 100 images per class (classes were originally imbalanced in the raw dataset, ranging from ~1,000 to 5,000+ images each).

**Two inference modes**, exposed by the `MineralIdentifier` model package:

- **`identify()`** — single best-guess identification via standard greedy text generation. Fast, but only ever gives one answer with no sense of how confident the model actually was.
- **`predict_top_k()`** — closed-set confidence scoring. Rather than freely generating an answer, this scores every one of the 15 known `{mineral_name, chemical_formula}` pairs against the image (via each candidate's average per-token log-likelihood), then ranks them with a softmax over the scores. This is what powers the "show top candidates" feature — genuine ranked confidence, not just a probability of the single token the model happened to generate.

The model logic lives in a self-contained Python package (`mineral_identifier`) with a `pyproject.toml`, so it can be built into a `.whl` file and installed with `pip install` independently of the rest of the project.

## Backend architecture (FastAPI)

The backend is a single FastAPI app that loads the fine-tuned model **once at process startup** (not per-request — reloading a 7B model per request would make every call take minutes) and keeps it in memory for the life of the process.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/predict/single` | POST | Upload an image + query, get back a single best-guess identification |
| `/predict/candidates` | POST | Upload an image + query, get back the top-K ranked candidates with confidence |
| `/log/single` | POST | Persist a completed single prediction to history |
| `/log/candidates` | POST | Persist a completed candidates prediction to history |
| `/log/all` | GET | Retrieve logged history, newest first |

A few architectural choices worth calling out:

- **`/predict/*` endpoints use `multipart/form-data`** (`UploadFile` + `Form` fields), since they carry an actual image file. **`/log/*` endpoints use plain JSON bodies** (Pydantic models), since they only carry the already-computed result plus metadata — no file involved.
- **Route handlers are defined as plain `def`, not `async def`.** Both model inference and Firestore writes are blocking calls; FastAPI automatically runs synchronous route functions in a threadpool, so a slow GPU inference call or network write doesn't block the event loop for other concurrent requests (like a health check hitting the server mid-inference).
- **Persistence uses Firebase/Firestore**, via the `firebase-admin` SDK. Logged entries are stored in an `Entities` collection, shaped to match the same `{id, image, conversations: [human, gpt]}` schema the training dataset itself uses — so logged real-world interactions could, in principle, be folded back into future training data without reformatting. Each entry also gets a server-side `created_at` timestamp, which is what `/log/all` orders by.
- **CORS is currently wide open** (`allow_origins=["*"]`) for local development; this should be tightened to the frontend's actual origin before any real deployment.

## Frontend architecture (React)

The frontend is React + TypeScript, using `react-router` for client-side routing and CSS Modules for styling (each page/component has its own scoped `*.module.css` file).

**Pages:**
- **HomePage** — project introduction, a short explanation of the AI problem being solved, and calls to action linking to Chat and History.
- **ChatPage** — the core interaction: pick a photo, optionally describe field observations, and get an identification (single answer or ranked candidates).
- **AboutPage** — model, dataset, and an honest limitations disclosure.
- **HistoryPage** — (in progress) intended to list past identifications via `/log/all`.
- **RegisterPage / LoginPage** — authentication (routes exist; not covered by this README's scope).

**Hooks (`src/hooks`):**
- **`useModel.ts`** — wraps `/predict/single` and `/predict/candidates`. Builds `FormData` for the image upload, exposes `loading`/`error` state, matching a consistent pattern used across the app's data-fetching hooks.
- **`useHistory.ts`** — wraps `/log/single`, `/log/candidates`, and `/log/all`. Logging calls are fired right after a prediction succeeds, deliberately fire-and-forget (a failure to log shouldn't block someone from seeing their prediction result).

**Design system:** kept intentionally simple and flat — off-white "paper" card backgrounds (`#F7F5F0`) for general content, a warm gold "important" variant (`#FBF0DC` background with a `#B98B2A` accent border) reserved for content that should draw the eye first (e.g. the Limitations section, a highlighted callout), and a consistent azurite blue (`#24507A`) for primary actions and active/pressed button states. Each page currently defines its own CSS module; shared patterns like `.Window` are duplicated across modules for now rather than centralized, which is a reasonable next refactor once more pages exist.

## Project structure

```
project/
├── model/                          # ML model package
│   ├── main.py                     # load_inference_model, identify_mineral,
│   │                                #   predict_top_k, score_candidates
│   └── training/
│       ├── train.py                # QLoRA fine-tuning script
│       ├── dataset.py               # generates the training JSON from Kaggle images
│       ├── llava_mineral_train.json
│       ├── llava-mineral-lora/     # trained adapter weights (output of train.py)
│       └── mineral-trier/          # held-out test images
├── mineral_identifier_pkg/         # installable pip package wrapping model/
│   └── src/mineral_identifier/
│       ├── model.py                # MineralIdentifier class
│       └── cli.py                  # `mineral-identify` command
├── backend/
│   ├── main.py                     # FastAPI app, /predict and /log routes
│   ├── firebase.py                 # Firestore client + basic doc helpers
│   └── handlers/
│       ├── model_handlers.py       # image-upload → model inference glue
│       └── db_handlers.py          # Entities collection read/write logic
└── frontend/
    └── src/
        ├── hooks/
        │   ├── useModel.ts
        │   └── useHistory.ts
        ├── components/
        │   ├── Header.tsx
        │   └── Router.tsx
        └── pages/
            ├── HomePage.tsx
            ├── ChatPage.tsx
            ├── AboutPage.tsx
            └── HistoryPage.tsx      # in progress
```

## Known limitations

These come directly from testing the fine-tuned model, not generic disclaimers — see `AboutPage.tsx` for the version shown to end users:

- **Closed set of known classes.** The model only recognizes the 15 mineral classes it was fine-tuned on. Shown something outside that set, it will still confidently return one of its known classes rather than indicate uncertainty about the category itself.
- **Confuses visually similar minerals.** Errors cluster among genuine look-alikes — pale colorless crystals (baryte/calcite/quartz), metallic-lustered minerals (pyrite/hematite), and other visually overlapping groups.
- **Small, curated training set.** 100 images per class, sourced from a Kaggle dataset of generally well-lit, uncluttered specimen photos. Real-world field photos (poor lighting, cluttered backgrounds, odd angles) haven't been specifically validated.
- **Confidence scores are relative, not calibrated.** The ranked-candidates feature scores likelihood *among the 15 known classes only* — it cannot express "none of these are right," and the percentages shouldn't be read as rigorously calibrated real-world probabilities.
- **Occasionally returns malformed JSON.** When this happens, the API and frontend fall back to showing the raw model output rather than crashing.

## Getting started

This section is a brief addition beyond the architecture description above — expand as the setup process solidifies.

**Backend:**
```
cd backend
pip install -r requirements.txt   # fastapi, uvicorn, transformers, peft, bitsandbytes, firebase-admin, etc.
uvicorn main:app --reload
```

**Frontend:**
```
cd frontend
npm install
npm run dev
```

The backend expects a trained LoRA adapter at the path configured in `model/main.py` (`training/llava-mineral-lora/`) — run `model/training/train.py` first if it doesn't exist yet — and a Firebase service account credentials file for the logging endpoints to work.