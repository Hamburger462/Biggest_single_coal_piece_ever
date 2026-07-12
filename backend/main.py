import json
from typing import List, Union

from fastapi import FastAPI

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import load_inference_model

from backend.handlers.model_handlers import identify_mineral_candidates, identify_user_mineral
from backend.handlers.db_handlers import log_single_prediction, log_candidate_predictions, get_all_entities

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model, processor = load_inference_model()



@app.get("/")
async def root():
    return {"message": "The server is currently up and running"}


@app.post("/predict/single")
def identify_endpoint(
    image: UploadFile = File(...),
    user_query: str = Form("What mineral is this?"),
):
    image_bytes = image.file.read()
    raw_output = identify_user_mineral(model, processor, image_bytes, user_query)
 
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # Model didn't return valid JSON this time - surface the raw text
        # rather than crashing the endpoint.
        return {"raw_output": raw_output}
    
    
@app.post("/predict/candidates")
def identify_candidates_endpoint(
    image: UploadFile = File(...),
    user_query: str = Form("What mineral is this?"),
    top_k: int = Form(3),
):
    image_bytes = image.file.read()
    results = identify_mineral_candidates(model, processor, image_bytes, user_query, top_k=top_k)
 
    return [
        {"mineral_name": name, "chemical_formula": formula, "confidence": pct}
        for name, formula, pct in results
    ]


# --------------------------------------------------------------------------
# Logging endpoints - the frontend calls these once it already has a result
# back from /predict/single or /predict/candidates and wants to save it
# (e.g. to show later on the History page).
# --------------------------------------------------------------------------

class SingleResultPayload(BaseModel):
    mineral_name: str
    chemical_formula: str


class RawOutputPayload(BaseModel):
    raw_output: str


class LogSinglePayload(BaseModel):
    image_name: str
    user_query: str
    # Accepts either a clean parsed result or the raw-text fallback shape
    # /predict/single can return if the model didn't produce valid JSON.
    result: Union[SingleResultPayload, RawOutputPayload]


class CandidateItem(BaseModel):
    mineral_name: str
    chemical_formula: str
    confidence: float


class LogCandidatesPayload(BaseModel):
    image_name: str
    user_query: str
    results: List[CandidateItem]


@app.post("/log/single")
def log_single_endpoint(payload: LogSinglePayload):
    entity = log_single_prediction(
        payload.image_name, payload.user_query, payload.result.dict()
    )
    return {"status": "logged", "id": entity["id"]}


@app.post("/log/candidates")
def log_candidates_endpoint(payload: LogCandidatesPayload):
    entity = log_candidate_predictions(
        payload.image_name,
        payload.user_query,
        [c.dict() for c in payload.results],
    )
    return {"status": "logged", "id": entity["id"]}


@app.get("/log/all")
def get_all_logs_endpoint(limit: int = 50):
    return get_all_entities(limit=limit)