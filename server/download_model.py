"""
Download DeepSeek model script for Render deployment
Downloads a GGUF model from HuggingFace to the models directory
"""

import os
import urllib.request
from pathlib import Path

# Model URLs (replace with actual GGUF model URLs)
MODELS = {
    "deepseek-llama-7b-q4": "https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF/resolve/main/deepseek-llama-7b-chat.Q4_K_M.gguf",
    "deepseek-coder-6.7b-q4": "https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF/resolve/main/deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
}


def download_model(model_name: str = "deepseek-llama-7b-q4", output_dir: str = "models"):
    """Download a model from HuggingFace"""
    if model_name not in MODELS:
        print(f"Available models: {list(MODELS.keys())}")
        return

    url = MODELS[model_name]
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    filename = url.split("/")[-1]
    filepath = output_path / filename

    print(f"Downloading {model_name}...")
    print(f"From: {url}")
    print(f"To: {filepath}")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded / total_size * 100, 100) if total_size > 0 else 0
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

    urllib.request.urlretrieve(url, filepath, progress_hook)
    print(f"\n\nModel saved to: {filepath}")

    # Create symlink for easy access
    symlink_path = output_path / "deepseek-llama.gguf"
    if symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to(filename)

    print(f"Symlink created: {symlink_path} -> {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download DeepSeek model")
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-llama-7b-q4",
        choices=list(MODELS.keys()),
        help="Model to download"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models",
        help="Output directory"
    )

    args = parser.parse_args()
    download_model(args.model, args.output)
