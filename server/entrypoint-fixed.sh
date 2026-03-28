#!/bin/bash
set -e

echo "=========================================="
echo "  DeepSeek Local AI Server - Starting"
echo "=========================================="

# Configuration
MODEL_DIR="/app/models"
MODEL_NAME="${MODEL_NAME:-deepseek-llama.gguf}"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"

# Create models directory
mkdir -p "$MODEL_DIR"

# Check if model exists and has content
if [ ! -s "$MODEL_PATH" ]; then
    echo "Model not found or empty. Downloading..."
    echo "Model will be saved to: $MODEL_PATH"

    # Try TinyLlama first (1.8GB, works on free tier)
    echo "Downloading TinyLlama 1.1B model..."
    if curl -L --connect-timeout 30 --max-time 600 \
        -o "$MODEL_PATH" \
        "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"; then
        echo "✓ Model downloaded successfully!"
    else
        echo "✗ Download failed. Trying alternate source..."
        # Fallback to mirror or different URL
        curl -L --connect-timeout 30 --max-time 600 \
            -o "$MODEL_PATH" \
            "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    fi

    # Verify download
    if [ -s "$MODEL_PATH" ]; then
        SIZE=$(du -h "$MODEL_PATH" | cut -f1)
        echo "✓ Model file size: $SIZE"
    else
        echo "✗ ERROR: Model file is empty or missing!"
        echo "Starting server without model (will fail on inference)..."
    fi
else
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "✓ Model found: $MODEL_PATH ($SIZE)"
fi

# Start the server
echo ""
echo "Starting server on port ${PORT:-8000}..."
echo "=========================================="

exec python main.py \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --n-gpu-layers 0
