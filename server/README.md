# DeepSeek Local AI Server

Run your own DeepSeek AI server locally on your hardware. No API keys, no cloud, complete privacy.

## Quick Start

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Download a Model

Download a DeepSeek model in GGUF format:

- Visit [HuggingFace Models](https://huggingface.co/models?search=deepseek)
- Download a `.gguf` format model
- Place it in `server/models/` directory

Recommended models:
- `deepseek-llama-7b-chat-q4.gguf` (4GB, fast)
- `deepseek-llama-13b-chat-q4.gguf` (8GB, balanced)
- `deepseek-llama-33b-chat-q4.gguf` (20GB, best quality)

### 3. Start the Server

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

**Or manually:**
```bash
python main.py --model models/deepseek-llama.gguf --port 8000
```

### 4. Use the Web UI

Open [http://localhost:8000/web/](http://localhost:8000/web/) in your browser!

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Server info |
| `GET /health` | Health check |
| `GET /v1/models` | List models |
| `POST /v1/chat/completions` | Chat completions (OpenAI-compatible) |
| `GET /docs` | API documentation (Swagger UI) |
| `GET /web/` | Web UI |

## Example Usage

### cURL
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Explain quantum computing"}
        ]
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [
      {role: 'user', content: 'Hello!'}
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## Configuration

Edit `config.yaml` to customize:

- Server host and port
- Model parameters
- Generation settings
- GPU acceleration

## Command Line Options

```bash
python main.py --help
```

- `--model PATH`: Path to model file
- `--host HOST`: Server host (default: 0.0.0.0)
- `--port PORT`: Server port (default: 8000)
- `--n-ctx N`: Context size (default: 2048)
- `--n-gpu-layers N`: GPU layers (default: -1 = all)

## Requirements

- Python 3.10+
- 8GB+ RAM (for 7B model)
- GPU with 4GB+ VRAM (optional, for acceleration)
- 10GB+ disk space

## Troubleshooting

**Model not loading:**
- Ensure model is in GGUF format
- Check file path is correct
- Verify sufficient RAM available

**Slow performance:**
- Enable GPU layers: `--n-gpu-layers -1`
- Use a quantized model (Q4 or Q5)
- Reduce context size: `--n-ctx 1024`

**Out of memory:**
- Use a smaller model
- Reduce GPU layers: `--n-gpu-layers 0`
- Decrease context size

## Features

- 🚀 Fast local inference
- 🔒 Complete privacy
- 🌐 OpenAI-compatible API
- 🎨 Beautiful web UI
- 💾 GPU acceleration
- 📊 Swagger documentation
- 🔧 Easy configuration

## License

MIT
