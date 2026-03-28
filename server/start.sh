#!/bin/bash

# DeepSeek Local AI Server - Startup Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  DeepSeek Local AI Server"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Create necessary directories
mkdir -p models
mkdir -p logs

# Check if model exists
MODEL_PATH="${MODEL_PATH:-models/deepseek-llama.gguf}"

if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${YELLOW}⚠${NC} Model not found at: $MODEL_PATH"
    echo ""
    echo "To get started, you need to download a DeepSeek model:"
    echo ""
    echo "1. Visit: https://huggingface.co/models"
    echo "2. Search for 'deepseek'"
    echo "3. Download a GGUF format model"
    echo "4. Place it in: models/deepseek-llama.gguf"
    echo ""
    echo "Or set MODEL_PATH environment variable to your model location."
    echo ""
    echo "Server will start without a model. You can load one later."
    echo ""
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment not found. Creating..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}✓${NC} Installing dependencies..."
pip install -q -r requirements.txt

# Start server
echo ""
echo -e "${GREEN}✓${NC} Starting server on http://localhost:8000"
echo ""
echo "API endpoints:"
echo "  - http://localhost:8000"
echo "  - http://localhost:8000/docs (API documentation)"
echo "  - http://localhost:8000/health (health check)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Set default model path
export MODEL_PATH="$MODEL_PATH"

# Start the server
python3 main.py \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port 8000 \
    --n-ctx 2048 \
    --n-gpu-layers -1
