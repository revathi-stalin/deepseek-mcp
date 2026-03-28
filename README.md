# DeepSeek MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with DeepSeek AI models.

## Features

- **Chat Completions**: Generate responses using DeepSeek's AI models
- **Model Listing**: Query available DeepSeek models
- **OpenAI-Compatible**: Uses DeepSeek's OpenAI-compatible API
- **Dual Output Formats**: JSON and Markdown responses
- **Async Operations**: Efficient async/await HTTP requests

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -e .
```

## Configuration

Set your DeepSeek API key as an environment variable:

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

Get your API key from [https://platform.deepseek.com/](https://platform.deepseek.com/)

## Usage

### Local Testing with MCP Inspector

```bash
DEEPSEEK_API_KEY=your-key python deepseek_mcp.py
```

Then open in MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python deepseek_mcp.py
```

### Streamable HTTP Transport

Run as an HTTP server on port 8000:

```bash
DEEPSEEK_API_KEY=your-key python deepseek_mcp.py --transport streamable_http --port 8000
```

## Available Tools

### deepseek_chat

Generate chat completions using DeepSeek AI models.

**Parameters:**
- `messages` (required): List of conversation messages with role and content
- `model` (optional): Model to use (default: "deepseek-chat")
  - Options: "deepseek-chat", "deepseek-coder"
- `temperature` (optional): Sampling temperature 0.0-2.0 (default: 1.0)
- `max_tokens` (optional): Maximum tokens to generate
- `top_p` (optional): Nucleus sampling 0.0-1.0 (default: 1.0)
- `response_format` (optional): Output format - "json" or "markdown" (default: "json")

**Example messages format:**
```json
[
  {"role": "system", "content": "You are a helpful assistant"},
  {"role": "user", "content": "Explain quantum computing"}
]
```

### deepseek_list_models

List available DeepSeek AI models.

**Parameters:**
- `response_format` (optional): Output format - "json" or "markdown" (default: "json")

## Available Models

- **deepseek-chat**: General-purpose chat model
- **deepseek-coder**: Code-focused model for programming tasks

## Error Handling

The server provides clear error messages for:
- Invalid API keys (401)
- Rate limiting (429)
- Invalid parameters (400)
- Network timeouts

## Requirements

- Python 3.10+
- httpx
- pydantic
- mcp

## License

MIT

# DeepSeek-V3 Fine-tuning Guide

Fine-tune DeepSeek-V3 (671B) on custom domain knowledge using LoRA/QLoRA.

## Fine-tuning Structure

```
deepseek_mcp/
├── data/                  # Training datasets
│   └── example_training_data.jsonl
├── models/                # Downloaded models
├── checkpoints/           # Saved checkpoints
├── logs/                  # Training logs
├── train.py              # Training script
├── inference.py          # Inference script
└── requirements.txt      # Dependencies
```

## Hardware Requirements

For DeepSeek-V3 (671B) with QLoRA:
- **Minimum:** 4x A100 (80GB) or equivalent
- **Recommended:** 8x A100 (80GB) or H100
- **Storage:** 2TB+ for model weights and checkpoints

## Fine-tuning Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Prepare your training data in `data/training_data.jsonl`:
```json
{"instruction": "Your question/task", "input": "context", "output": "expected answer"}
```

3. Run training:
```bash
python train.py
```

4. Run inference:
```bash
python inference.py
```

## Training Tips

- Start with smaller LoRA rank (r=8) for faster training
- Use gradient checkpointing to save memory
- Monitor with Weights & Biases (wandb)
- Adjust batch size based on GPU memory
- Use multi-GPU with DeepSpeed for faster training

---

# Deploy to Render

Deploy your fine-tuned DeepSeek model as a production API on Render.

## Render Deployment

### Quick Deploy

1. **Push to GitHub** (already done!)
2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `revathi-stalin/deepseek-mcp`

3. **Configure:**
   - **Runtime:** Docker
   - **Build Context:** `.`
   - **Dockerfile:** `./Dockerfile`
   - **Plan:** Standard (recommended for model inference)

4. **Environment Variables:**
   ```bash
   BASE_MODEL_PATH=deepseek-ai/DeepSeek-V3
   LORA_PATH=/app/models/lora
   PORT=8000
   ```

5. **Deploy!** Render will build and deploy your API.

### Using render.yaml (Automatic)

For automatic deployment setup, the `render.yaml` file is configured. Just push to GitHub and connect in Render.

### Test Your Deployed API

```bash
# Replace with your Render URL
curl https://your-app.onrender.com/health

# Test chat completion
curl -X POST https://your-app.onrender.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

Or use the test script:
```bash
python api/test_api.py https://your-app.onrender.com
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Generate chat completions |

## Project Structure

```
deepseek_mcp/
├── api/                    # Inference API
│   ├── app.py             # FastAPI application
│   ├── requirements.txt   # API dependencies
│   └── test_api.py        # API testing script
├── Dockerfile             # Container configuration
├── render.yaml            # Render deployment config
├── .env.example           # Environment variables template
└── .renderignore          # Files to exclude from deployment

---

# 🚀 Run Your Own Local AI Server

Run DeepSeek models locally on your own hardware with complete privacy. No API keys, no cloud.

## Quick Start

### 1. Install Server Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Download a Model

Download a DeepSeek model in GGUF format from [HuggingFace](https://huggingface.co/models?search=deepseek):

```bash
# Create models directory
mkdir -p server/models

# Download a model (example links)
# - deepseek-llama-7b-chat-q4.gguf (~4GB)
# - deepseek-llama-13b-chat-q4.gguf (~8GB)
```

Place the downloaded model in `server/models/`

### 3. Start the Server

**Linux/Mac:**
```bash
cd server
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
cd server
start.bat
```

**Manual start:**
```bash
cd server
python main.py --model models/deepseek-llama.gguf --port 8000
```

### 4. Use the Web UI

Open [http://localhost:8000/web/](http://localhost:8000/web/) in your browser!

## Features

- 🚀 Fast local inference
- 🔒 Complete privacy (no cloud)
- 🌐 OpenAI-compatible API
- 🎨 Beautiful web UI
- 💾 GPU acceleration
- 📊 Swagger documentation

## Server API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Server information |
| `GET /health` | Health check |
| `GET /v1/models` | List available models |
| `POST /v1/chat/completions` | Chat completions |
| `GET /docs` | API documentation (Swagger) |
| `GET /web/` | Web UI |

## Requirements

- Python 3.10+
- 8GB+ RAM (for 7B model)
- GPU with 4GB+ VRAM (optional)
- 10GB+ disk space

For more details, see [server/README.md](server/README.md)
```
