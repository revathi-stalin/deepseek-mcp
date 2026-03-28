"""
Inference script for fine-tuned DeepSeek-V3 model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Configuration
BASE_MODEL = "deepseek-ai/DeepSeek-V3"
LORA_PATH = "checkpoints/deepseek-v3-lora"


def load_fine_tuned_model(base_model_path, lora_path):
    """Load the fine-tuned model for inference"""
    print("Loading base model...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(base_model, lora_path)
    model = model.merge_and_unload()  # Merge weights for faster inference

    return model, tokenizer


def generate_response(model, tokenizer, instruction, input_text="", max_new_tokens=512):
    """Generate a response from the fine-tuned model"""
    prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the response part
    response = response.split("### Response:")[1].strip()
    return response


def main():
    """Interactive inference loop"""
    model, tokenizer = load_fine_tuned_model(BASE_MODEL, LORA_PATH)
    print("\n" + "="*50)
    print("DeepSeek-V3 Fine-tuned Model Ready")
    print("="*50 + "\n")

    while True:
        instruction = input("Instruction (or 'quit' to exit): ")
        if instruction.lower() == 'quit':
            break

        input_text = input("Input (press Enter for none): ")

        print("\nGenerating response...")
        response = generate_response(model, tokenizer, instruction, input_text)
        print(f"\nResponse:\n{response}\n")
        print("-"*50 + "\n")


if __name__ == "__main__":
    main()
