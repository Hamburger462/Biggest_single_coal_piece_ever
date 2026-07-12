import os
import re
import sys
import torch
import json
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
from peft import PeftModel

# --- CONFIGURATION PATHS ---
BASE_MODEL_ID = "llava-hf/llava-1.5-7b-hf"

# Anchor to this script's own location on disk, rather than a plain relative
# path, so it resolves correctly no matter what directory you launch
# `python main.py` from. This points at the final adapter written by
# train.py's `model.save_pretrained(OUTPUT_DIR)` call at the end of
# training (not an intermediate `checkpoint-XXXX` folder).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LORA_ADAPTER_DIR = os.path.join(SCRIPT_DIR, "training", "llava-mineral-lora")
TRAIN_JSON = os.path.join(SCRIPT_DIR, "training", "llava_mineral_train.json")

# Confidence-scoring defaults (see predict_top_k / score_candidates below)
TOP_K = 3
TEMPERATURE = 0.3  # lower = sharper/more decisive confidence spread,
                    # higher = closer to uniform across candidates


def load_inference_model():
    if not os.path.isdir(LORA_ADAPTER_DIR):
        raise FileNotFoundError(
            f"No trained adapter found at {LORA_ADAPTER_DIR}. "
            "Run training/train.py to completion first - it saves the "
            "final adapter there at the end of the run."
        )

    print("Loading fine-tuned processor configuration...")
    # Loaded directly from your saved folder to grab your custom chat template/tokenizer settings
    processor = AutoProcessor.from_pretrained(LORA_ADAPTER_DIR)

    # Wrap 4-bit loading inside a proper configuration object.
    # bfloat16 here matches what train.py now trains with, so inference
    # numerics match training numerics.
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    print("Loading base vision model...")
    model = LlavaForConditionalGeneration.from_pretrained(
        BASE_MODEL_ID,
        quantization_config=quantization_config,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    print(f"Loading fine-tuned mineral adapter from {LORA_ADAPTER_DIR}...")
    # Explicitly bind the LoRA adapter directory to the model instance
    model = PeftModel.from_pretrained(model, LORA_ADAPTER_DIR, adapter_name="default")
    model.eval()  # Set to evaluation mode

    return model, processor


def identify_mineral(model, processor, image_path, user_query="What mineral is this?"):
    if not os.path.exists(image_path):
        return f"Error: Image not found at {image_path}"

    # Open and format target image
    image = Image.open(image_path).convert("RGB")

    # Build a structured conversation list matching the standard Hugging Face schema
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {"type": "image"},
            ],
        }
    ]

    # Use the chat template you fine-tuned on to seamlessly append the text markers
    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)

    # Process inputs for the GPU using the processed template
    inputs = processor(text=prompt, images=image, return_tensors="pt").to("cuda")

    print("Analyzing specimen...")
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=120,   # Kept near ~120 to fit the target JSON schema
            do_sample=False,      # Disables random creativity
            use_cache=True
        )

    # Isolate only the model's new tokens (the response)
    input_token_len = inputs["input_ids"].shape[1]
    generated_tokens = output_ids[0][input_token_len:]
    response_text = processor.decode(generated_tokens, skip_special_tokens=True).strip()

    return response_text


# --------------------------------------------------------------------------
# Confidence scoring: rank known classes by likelihood instead of just
# taking generate()'s single best guess.
#
# Rather than freely generating an answer, this scores every known
# {mineral_name, chemical_formula} pair (pulled from training data) against
# the image - i.e. "if the answer were Baryte, how surprised would the
# model be? What about Calcite? Quartz?" - and ranks them. This works
# because a language model can compute the exact probability it would have
# assigned to any specific candidate text, not just the text it happens to
# generate on its own.
#
# Caveat: these are relative likelihoods among the known classes, not
# rigorously calibrated real-world probabilities, and this method has no
# way to say "none of these" - it will always rank among the known set.
# --------------------------------------------------------------------------

def load_class_ground_truth(train_json_path=TRAIN_JSON):
    """Build a {test_folder_name_lower: {"name": ..., "formula": ...}} map
    by reading each training entry's actual class folder (from its image
    path, e.g. "data\\azurite\\img.jpg" -> "azurite") and pairing it with
    whatever mineral_name/chemical_formula that class was actually trained
    with. This avoids assuming the folder name always matches the trained
    label exactly (e.g. folder "copper" but trained label "Native Copper")."""
    class_truth = {}
    if not os.path.isfile(train_json_path):
        print(f"WARNING: could not find {train_json_path} - ground truth checks will be skipped.")
        return class_truth

    with open(train_json_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    for entry in entries:
        parts = re.split(r"[\\/]+", entry["image"])
        if len(parts) < 2:
            continue
        folder = parts[-2].lower()

        gpt_value = entry["conversations"][1]["value"]
        try:
            parsed = json.loads(gpt_value)
        except json.JSONDecodeError:
            continue

        name = str(parsed.get("mineral_name", "")).strip()
        formula = str(parsed.get("chemical_formula", "")).strip()
        if name and folder not in class_truth:
            class_truth[folder] = {"name": name, "formula": formula}

    return class_truth


def build_candidate_list(train_json_path=TRAIN_JSON):
    """Returns a deduplicated list of (mineral_name, chemical_formula)
    pairs, one per known class, pulled straight from training data."""
    class_truth = load_class_ground_truth(train_json_path)
    seen = {}
    for info in class_truth.values():
        seen[info["name"]] = info["formula"]
    return list(seen.items())


def score_candidates(model, processor, image_path, user_query, candidates, temperature=TEMPERATURE):
    """Scores each (mineral_name, chemical_formula) candidate against the
    image and returns [(name, formula, confidence_pct), ...] sorted by
    confidence descending, where confidence_pct values sum to 1.0."""
    image = Image.open(image_path).convert("RGB")

    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {"type": "image"},
            ],
        }
    ]
    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)

    # Encode the prompt alone (with the image, so "<image>" expands the same
    # way it will below) to find where each candidate answer starts.
    prompt_ids = processor(text=prompt, images=image, return_tensors="pt")["input_ids"][0]
    prompt_len = prompt_ids.shape[0]

    avg_log_likelihoods = []
    for name, formula in candidates:
        answer_text = json.dumps({"mineral_name": name, "chemical_formula": formula}, indent=2)
        full_text = prompt.rstrip() + " " + answer_text

        encoded = processor(text=full_text, images=image, return_tensors="pt").to("cuda")
        labels = encoded["input_ids"].clone()
        labels[0, :prompt_len] = -100

        with torch.no_grad():
            # HF returns the mean cross-entropy loss over non-masked
            # (i.e. non -100) label tokens - exactly the average
            # per-token negative log-likelihood of this candidate answer.
            outputs = model(**encoded, labels=labels)

        avg_log_likelihoods.append(-outputs.loss.item())

    scores = torch.tensor(avg_log_likelihoods)
    probs = torch.softmax(scores / temperature, dim=0).tolist()

    ranked = sorted(zip(candidates, probs), key=lambda x: -x[1])
    return [(name, formula, pct) for (name, formula), pct in ranked]


def predict_top_k(model, processor, image_path, user_query="What mineral is this?", top_k=TOP_K, candidates=None):
    """Convenience wrapper: scores against all known classes (or a custom
    candidate list) and returns just the top_k [(name, formula, pct), ...]."""
    if candidates is None:
        candidates = build_candidate_list()
    ranked = score_candidates(model, processor, image_path, user_query, candidates)
    return ranked[:top_k]
