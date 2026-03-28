"""
DeepSeek-V3 LoRA Fine-tuning Script
Fine-tunes DeepSeek-V3 on custom domain knowledge using QLoRA
"""

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
import bitsandbytes as bnb

# Configuration
MODEL_NAME = "deepseek-ai/DeepSeek-V3"  # Update with actual model path
DATA_PATH = "data/training_data.jsonl"
OUTPUT_DIR = "checkpoints/deepseek-v3-lora"

# LoRA Configuration
LORA_CONFIG = {
    "r": 16,              # LoRA rank (higher = more parameters)
    "lora_alpha": 32,     # LoRA scaling
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# Training Configuration
TRAINING_CONFIG = {
    "output_dir": OUTPUT_DIR,
    "num_train_epochs": 3,
    "per_device_train_batch_size": 2,
    "per_device_eval_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "learning_rate": 2e-4,
    "weight_decay": 0.01,
    "warmup_steps": 100,
    "logging_steps": 10,
    "save_steps": 500,
    "eval_steps": 500,
    "save_total_limit": 3,
    "fp16": True,
    "gradient_checkpointing": True,
    "optim": "paged_adamw_32bit",
    "lr_scheduler_type": "cosine",
    "report_to": "wandb"
}


def load_model_and_tokenizer():
    """Load DeepSeek-V3 model with 4-bit quantization"""
    print(f"Loading model: {MODEL_NAME}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        use_fast=False
    )
    tokenizer.pad_token = tokenizer.eos_token

    # Load model with 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_4bit=True,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)

    # Add LoRA adapters
    lora_config = LoraConfig(**LORA_CONFIG)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model, tokenizer


def load_training_data(data_path, tokenizer, max_length=2048):
    """Load and prepare training dataset"""
    # Load your custom dataset
    # Format: {"instruction": "...", "input": "...", "output": "..."}
    dataset = load_dataset("json", data_files=data_path, split="train")

    def format_prompt(example):
        # Format for instruction tuning
        prompt = f"""### Instruction:
{example['instruction']}

### Input:
{example.get('input', '')}

### Response:
{example['output']}"""
        return prompt

    def tokenize_function(examples):
        prompts = [format_prompt(ex) for ex in examples]
        return tokenizer(
            prompts,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors=None
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )

    return tokenized_dataset


def main():
    """Main training function"""
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()

    # Load training data
    train_dataset = load_training_data(DATA_PATH, tokenizer)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8
    )

    # Training arguments
    training_args = TrainingArguments(**TRAINING_CONFIG)

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save final model
    print(f"Saving model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("Training complete!")


if __name__ == "__main__":
    main()
