import json

from fastapi import FastAPI

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from model import load_inference_model

from backend.handlers.model_handlers import identify_mineral_candidates, identify_user_mineral

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