#!/bin/bash
set -e

echo "Starting DeepSeek Local AI Server..."

# Check if model exists, download if not
MODEL_PATH="${MODEL_PATH:-models/deepseek-llama.gguf}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found. Downloading..."
    mkdir -p models

    # Download TinyLlama model for free tier (1.8GB)
    curl -L -o "$MODEL_PATH" \
      "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

    echo "Model downloaded successfully!"
    ls -lh "$MODEL_PATH"
else
    echo "Model found at: $MODEL_PATH"
fi

# Start the server
echo "Starting server on port ${PORT:-8000}..."
exec python main.py \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --n-gpu-layers 0
