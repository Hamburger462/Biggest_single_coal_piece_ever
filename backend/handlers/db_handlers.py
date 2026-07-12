import json
import uuid

from firebase_admin import firestore

from firebase import db, setDoc

ENTITIES_COLLECTION = "Entities"


def _generate_entity_id() -> str:
    return f"min_{uuid.uuid4().hex[:6]}"


def _build_entity(image_name: str, user_query: str, gpt_value: str) -> dict:
    return {
        "id": _generate_entity_id(),
        "image": image_name,
        "conversations": [
            {"from": "human", "value": f"<image>\n{user_query}"},
            {"from": "gpt", "value": gpt_value},
        ],
        "created_at": firestore.SERVER_TIMESTAMP,
    }


def log_single_prediction(image_name: str, user_query: str, result: dict) -> dict:
    gpt_value = json.dumps(result, indent=2)
    entity = _build_entity(image_name, user_query, gpt_value)
    setDoc(ENTITIES_COLLECTION, entity["id"], entity)
    return entity


def log_candidate_predictions(image_name: str, user_query: str, results: list) -> dict:
    """Logs the top-ranked candidate as the answer, in the same shape as a
    single prediction, but keeps the full ranked list alongside it under
    a "candidates" field for later review (e.g. checking whether the
    correct answer showed up further down the ranking)."""
    top = results[0] if results else {}
    gpt_value = json.dumps(
        {
            "mineral_name": top.get("mineral_name"),
            "chemical_formula": top.get("chemical_formula"),
        },
        indent=2,
    )
    entity = _build_entity(image_name, user_query, gpt_value)
    entity["candidates"] = results
    setDoc(ENTITIES_COLLECTION, entity["id"], entity)
    return entity


def get_all_entities(limit: int = 50) -> list:
    """Returns logged entities ordered youngest to oldest (most recently
    created first). Capped at `limit` since an uncapped history feed
    would only grow over time."""
    docs = (
        db.collection(ENTITIES_COLLECTION)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]