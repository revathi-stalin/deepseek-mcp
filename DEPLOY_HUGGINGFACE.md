# Deploy to HuggingFace Spaces (Free, 16GB RAM)

## Quick Deploy

### 1. Create HuggingFace Account
Go to [huggingface.co](https://huggingface.co) and sign up (free)

### 2. Create a New Space
1. Click **"New Space"** button
2. Fill in:
   - **Owner:** Your username
   - **Space name:** `deepseek-server`
   - **License:** MIT
   - **SDK:** Docker
   - **Hardware:** CPU-basic (free, 16GB RAM)

### 3. Connect GitHub Repository
1. Scroll to "Files"
2. Click **"Git clone"**
3. Or use the web interface to upload files

### 4. Create these files in your Space:

**README.md** (copy from this repo)
```yaml
---
title: DeepSeek AI Server
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---
```

**Dockerfile** (use Dockerfile.huggingface content)

**main.py**, **config.yaml**, **web/** from server/

### 5. Deploy!
The Space will automatically build and start. Wait 5-10 minutes for the model to download.

## Alternative: Push from Git

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/deepseek-server
cd deepseek-server

# Copy files from this repo
cp -r server/* .
cp README.md ../README.md ./

# Commit and push
git add .
git commit -m "Add DeepSeek server"
git push
```

## Your Server URL

```
https://huggingface.co/spaces/YOUR_USERNAME/deepseek-server
```

## Features on HuggingFace Spaces

| Feature | Available |
|---------|-----------|
| RAM | 16GB (Free) |
| CPU | 8 vCPUs (Free) |
| Storage | 50GB |
| Custom Domain | Yes |
| API Access | Yes |
| Public/Private | Both |
| Cost | FREE |

## Test Your Server

```bash
curl https://YOUR_USERNAME-deepseek-server.hf.space/health

curl -X POST https://YOUR_USERNAME-deepseek-server.hf.space/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Why HuggingFace Spaces?

✅ **Free** - No credit card needed
✅ **16GB RAM** - Enough for 7B models
✅ **Easy** - Deploy from GitHub
✅ **Fast** - Good CPU performance
✅ **Public API** - Share your model
✅ **Community** - Discover other models

## Compare Platforms

| Platform | RAM | Cost | GPU | Setup Time |
|----------|-----|------|-----|------------|
| **HuggingFace** | 16GB | **Free** | Paid | 5 min |
| Render | 512MB | Free | No | Failed |
| Render | 8GB | $7/mo | No | 5 min |
| RunPod | Variable | $0.20/hr | Yes | 10 min |
| Modal | Variable | Pay/use | Yes | 15 min |
