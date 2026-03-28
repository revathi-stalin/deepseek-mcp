#!/bin/bash
set -e

echo "Starting DeepSeek Local AI Server..."

# Check if model exists, download if not
MODEL_PATH="${MODEL_PATH:-models/deepseek-llama.gguf}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found. Downloading..."
    mkdir -p models

    # Download model (4.3GB, may take 10-20 minutes)
    curl -L -o "$MODEL_PATH" \
      "https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF/resolve/main/deepseek-llama-7b-chat.Q4_K_M.gguf"

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
