"""
test_model.py
Batch-evaluates the fine-tuned LLaVA mineral model against held-out images
in training/mineral-trier/<class>/*, using a mix of query phrasings, and
reports per-class accuracy for both mineral_name and chemical_formula.

Place this file next to main.py and run:
    python test_model.py

Ground-truth chemical formulas are pulled automatically from
training/llava_mineral_train.json (one lookup per class, from whatever
formula that class was trained with), so nothing needs to be hardcoded.
Ground-truth mineral names come from the subfolder names under
mineral-trier (e.g. "quartz", "wulfenite").
"""

import os
import json
import random

from main import load_inference_model, identify_mineral, SCRIPT_DIR, load_class_ground_truth, TRAIN_JSON

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
TEST_ROOT = os.path.join(SCRIPT_DIR, "training", "mineral-trier")
MAX_PER_CLASS = 5          # how many held-out images to test per class
SEED = 42

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# Deliberately varied phrasings, including some styles not necessarily
# mirrored exactly in the training set, to probe robustness to wording
# rather than just re-testing the training prompt distribution.
QUERIES = [
    "What mineral is this?",
    "Identify this specimen.",
    "Can you tell me what this rock is?",
    "Please identify the mineral shown in the image.",
    "What is this geological specimen?",
    "Name this mineral and give its formula.",
]


def collect_test_images(test_root, max_per_class, seed):
    """Returns {class_name: [image_path, ...]} sampled from mineral-trier."""
    random.seed(seed)
    class_images = {}

    if not os.path.isdir(test_root):
        raise FileNotFoundError(f"Test image folder not found: {test_root}")

    for class_name in sorted(os.listdir(test_root)):
        class_dir = os.path.join(test_root, class_name)
        if not os.path.isdir(class_dir):
            continue

        images = [
            os.path.join(class_dir, f)
            for f in os.listdir(class_dir)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]
        if not images:
            continue

        random.shuffle(images)
        class_images[class_name] = images[:max_per_class]

    return class_images


def try_parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def main():
    ground_truth = load_class_ground_truth(TRAIN_JSON)
    class_images = collect_test_images(TEST_ROOT, MAX_PER_CLASS, SEED)

    if not class_images:
        print(f"No test images found under {TEST_ROOT}")
        return

    total_classes = len(class_images)
    total_images = sum(len(v) for v in class_images.values())
    print(f"Found {total_images} held-out test images across {total_classes} classes.")
    print("Loading model (this can take a minute)...\n")

    model, processor = load_inference_model()

    # Per-class tallies: [name_correct, formula_correct, total, invalid_json]
    results = {}
    mismatches = []  # detailed log of anything that didn't match, for inspection

    query_cycle_idx = 0
    for class_name, image_paths in class_images.items():
        results[class_name] = {"name_correct": 0, "formula_correct": 0, "total": 0, "invalid_json": 0}
        truth = ground_truth.get(class_name.lower())
        expected_name = truth["name"].strip().lower() if truth else class_name.lower()
        expected_formula = truth["formula"] if truth else None
        if truth is None:
            print(f"WARNING: no training data found for folder '{class_name}' - "
                  f"falling back to raw folder name as ground truth.")

        for image_path in image_paths:
            query = QUERIES[query_cycle_idx % len(QUERIES)]
            query_cycle_idx += 1

            raw_output = identify_mineral(model, processor, image_path, query)
            parsed = try_parse_json(raw_output)

            results[class_name]["total"] += 1

            if parsed is None:
                results[class_name]["invalid_json"] += 1
                mismatches.append({
                    "class": class_name,
                    "image": os.path.basename(image_path),
                    "query": query,
                    "issue": "invalid_json",
                    "raw_output": raw_output,
                })
                continue

            predicted_name = str(parsed.get("mineral_name", "")).strip().lower()
            predicted_formula = str(parsed.get("chemical_formula", "")).strip()

            name_ok = predicted_name == expected_name
            if name_ok:
                results[class_name]["name_correct"] += 1

            formula_ok = None
            if expected_formula is not None:
                formula_ok = predicted_formula == expected_formula
                if formula_ok:
                    results[class_name]["formula_correct"] += 1

            if not name_ok or formula_ok is False:
                mismatches.append({
                    "class": class_name,
                    "image": os.path.basename(image_path),
                    "query": query,
                    "issue": "mismatch",
                    "predicted_name": predicted_name,
                    "predicted_formula": predicted_formula,
                    "expected_formula": expected_formula,
                })

            status = "OK" if name_ok and formula_ok is not False else "MISS"
            print(f"[{status}] {class_name:15s} | query: \"{query[:40]}\" | got: {predicted_name}")

    # --------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PER-CLASS RESULTS")
    print("=" * 70)
    print(f"{'Class':<20}{'Name Acc':<12}{'Formula Acc':<14}{'Invalid JSON':<14}")

    total_name_correct = 0
    total_formula_correct = 0
    total_formula_checked = 0
    total_all = 0

    for class_name, r in results.items():
        name_acc = r["name_correct"] / r["total"] if r["total"] else 0
        formula_denom = r["total"] - r["invalid_json"]
        formula_acc = (r["formula_correct"] / formula_denom) if formula_denom else 0
        print(
            f"{class_name:<20}{name_acc:>6.0%} ({r['name_correct']}/{r['total']})   "
            f"{formula_acc:>6.0%} ({r['formula_correct']}/{formula_denom})   "
            f"{r['invalid_json']}"
        )
        total_name_correct += r["name_correct"]
        total_formula_correct += r["formula_correct"]
        total_formula_checked += formula_denom
        total_all += r["total"]

    print("-" * 70)
    overall_name_acc = total_name_correct / total_all if total_all else 0
    overall_formula_acc = total_formula_correct / total_formula_checked if total_formula_checked else 0
    print(f"OVERALL: name accuracy {overall_name_acc:.0%} ({total_name_correct}/{total_all}), "
          f"formula accuracy {overall_formula_acc:.0%} ({total_formula_correct}/{total_formula_checked})")

    if mismatches:
        print("\n" + "=" * 70)
        print(f"DETAILS ON {len(mismatches)} MISSES / ISSUES")
        print("=" * 70)
        for m in mismatches:
            print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()