"""
train.py
QLoRA fine-tuning of LLaVA-v1.5-7B on the mineral identification dataset
produced by dataset.py (llava_mineral_train.json).

Designed for a single Windows machine with an 8GB-class GPU (e.g. RTX 3070)
using bitsandbytes 4-bit quantization + a LoRA adapter, so only a small
number of trainable parameters and activations need to fit in VRAM.

--------------------------------------------------------------------------
SETUP (Windows, PowerShell)
--------------------------------------------------------------------------
1. Create and activate a virtual environment:
     python -m venv llava-env
     .\llava-env\Scripts\activate

2. Install PyTorch with CUDA support (match to your installed CUDA driver;
   this example targets CUDA 12.1 - check https://pytorch.org/get-started/locally/
   if you have a different driver):
     pip install torch --index-url https://download.pytorch.org/whl/cu121

3. Install the rest:
     pip install transformers accelerate peft bitsandbytes pillow

   Note: bitsandbytes added official Windows wheels from ~0.43 onward.
   If `pip install bitsandbytes` fails to find CUDA, upgrade it explicitly:
     pip install -U bitsandbytes

4. Make sure your folder layout looks like this (matches dataset.py):
     project/
       train.py
       llava_mineral_train.json   <- produced by dataset.py
       data/
         azurite/
           img1.jpg
           ...
         baryte/
           ...

5. Run training:
     python train.py

   Checkpoints (LoRA adapter only) are written to ./llava-mineral-lora/
--------------------------------------------------------------------------
"""

import os
import json
import random

import torch
from torch.utils.data import Dataset
from PIL import Image

from transformers import (
    AutoProcessor,
    LlavaForConditionalGeneration,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


# --------------------------------------------------------------------------
# Config - tuned for an 8GB GPU (RTX 3070). Adjust if you change hardware.
# --------------------------------------------------------------------------
MODEL_ID = "llava-hf/llava-1.5-7b-hf"
DATA_JSON = "./llava_mineral_train.json"
DATA_ROOT = "."  # image paths in the JSON are like "data/azurite/img.jpg"
OUTPUT_DIR = "./llava-mineral-lora"

MAX_LENGTH = 750     # truncate text (image tokens + prompt + JSON answer)
PER_DEVICE_BATCH_SIZE = 1  # keep at 1 on 8GB cards
GRAD_ACCUM_STEPS = 8       # effective batch size = 1 * 8 = 8
NUM_EPOCHS = 2
LEARNING_RATE = 2e-4
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
SEED = 42


def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# --------------------------------------------------------------------------
# Dataset
# --------------------------------------------------------------------------
class LlavaMineralDataset(Dataset):
    """
    Reads the JSON produced by dataset.py:
      [
        {
          "id": "...",
          "image": "data/azurite/img.jpg",
          "conversations": [
            {"from": "human", "value": "<image>\\nWhat mineral is this?"},
            {"from": "gpt", "value": "{...json...}"}
          ]
        },
        ...
      ]
    and turns each entry into a LLaVA v1.5 prompt:
      "USER: <image>\\n{question} ASSISTANT: {answer}"
    with labels masked (-100) over everything except the assistant's answer,
    so the model only learns to produce the JSON response.
    """

    def __init__(self, json_path, data_root, processor, max_length=512):
        with open(json_path, "r", encoding="utf-8") as f:
            self.entries = json.load(f)
        self.data_root = data_root
        self.processor = processor
        self.max_length = max_length

        # Filter out any entries whose image is missing on disk, rather than
        # crashing mid-training on a bad path.
        valid = []
        for e in self.entries:
            img_path = os.path.join(self.data_root, e["image"])
            if os.path.isfile(img_path):
                valid.append(e)
        skipped = len(self.entries) - len(valid)
        if skipped:
            print(f"Skipping {skipped} entries with missing image files.")
        self.entries = valid

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        entry = self.entries[idx]
        img_path = os.path.join(self.data_root, entry["image"])
        image = Image.open(img_path).convert("RGB")

        human_turn = entry["conversations"][0]["value"]  # already has "<image>\n..."
        question = human_turn.replace("<image>\n", "").strip()
        answer = entry["conversations"][1]["value"]

        prompt_only = f"USER: <image>\n{question} ASSISTANT:"
        full_text = f"{prompt_only} {answer}"

        # Tokenize the prompt alone first, to know where the answer starts
        # so we can mask everything before it out of the loss.
        prompt_ids = self.processor.tokenizer(
            prompt_only, add_special_tokens=True
        )["input_ids"]

        encoded = self.processor(
            text=full_text,
            images=image,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
        )

        input_ids = encoded["input_ids"][0]
        attention_mask = encoded["attention_mask"][0]
        pixel_values = encoded["pixel_values"][0]

        labels = input_ids.clone()
        prompt_len = min(len(prompt_ids), self.max_length)
        labels[:prompt_len] = -100
        # Also mask out padding tokens
        pad_token_id = self.processor.tokenizer.pad_token_id
        labels[input_ids == pad_token_id] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "pixel_values": pixel_values,
            "labels": labels,
        }


def main():
    set_seed(SEED)

    if not torch.cuda.is_available():
        print(
            "WARNING: No CUDA GPU detected. This script is configured for "
            "4-bit GPU training and will be extremely slow or fail on CPU."
        )

    print(f"Loading processor and model: {MODEL_ID}")
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    if processor.tokenizer.pad_token is None:
        processor.tokenizer.pad_token = processor.tokenizer.unk_token or processor.tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = LlavaForConditionalGeneration.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.config.use_cache = False

    model = prepare_model_for_kbit_training(model)

    # Target the language-model attention/MLP projections. Leaving the
    # vision tower and projector frozen keeps trainable params (and VRAM)
    # small while still adapting how the model talks about what it sees.
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("Building dataset...")
    train_dataset = LlavaMineralDataset(
        json_path=DATA_JSON,
        data_root=DATA_ROOT,
        processor=processor,
        max_length=MAX_LENGTH,
    )
    print(f"Loaded {len(train_dataset)} training examples.")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        fp16=True,
        gradient_checkpointing=True,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=False,
        dataloader_num_workers=0,  # safer default on Windows
        optim="paged_adamw_8bit",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving LoRA adapter to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()