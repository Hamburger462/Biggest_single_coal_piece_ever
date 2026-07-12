import os
import json
import tempfile

from model import identify_mineral, predict_top_k

def _save_temp_image(image_bytes, suffix=".jpg"):
    """Writes uploaded image bytes to a temp file, since identify_mineral
    and predict_top_k expect a file path, not raw bytes."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        return tmp.name
 
 
def identify_user_mineral(model, processor, image_bytes, user_query):
    """Single best-guess identification. Returns the raw model output
    (should be a JSON string like {"mineral_name": ..., "chemical_formula": ...})."""
    tmp_path = _save_temp_image(image_bytes)
    print(user_query)
    try:
        return identify_mineral(model, processor, tmp_path, user_query)
    finally:
        os.remove(tmp_path)
 
 
def identify_mineral_candidates(model, processor, image_bytes, user_query, top_k=3):
    """Ranked, confidence-scored predictions across all known classes.
    Returns [(name, formula, confidence_pct), ...]."""
    tmp_path = _save_temp_image(image_bytes)
    print(user_query)
    try:
        return predict_top_k(model, processor, tmp_path, user_query, top_k=top_k)
    finally:
        os.remove(tmp_path)