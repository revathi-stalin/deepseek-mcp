---
title: DeepSeek Local AI Server
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# DeepSeek Local AI Server

Run DeepSeek models locally with this AI server.

## 🚀 Quick Start

Click the **"Running"** status above to launch the server!

## Features

- 🤖 Run DeepSeek & LLaMA models locally
- 💬 Chat completions API
- 🌐 Beautiful web UI
- 📊 OpenAI-compatible endpoints

## API Endpoints

- `GET /` - Server info
- `GET /health` - Health check
- `GET /v1/models` - List models
- `POST /v1/chat/completions` - Chat completions
- `GET /web/` - Web UI

## Usage

### Python
```python
import requests

response = requests.post(
    "https://your-space.hf.space/v1/chat/completions",
    json={"messages": [{"role": "user", "content": "Hello!"}]}
)
print(response.json())
```

### cURL
```bash
curl -X POST https://your-space.hf.space/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Hardware

- CPU: 8 vCPUs (HuggingFace Spaces)
- RAM: 16GB
- Storage: 50GB

## License

MIT
