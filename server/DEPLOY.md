# Deploy DeepSeek Server to Render

Deploy your local DeepSeek AI server to Render cloud.

## Prerequisites

1. A [Render](https://render.com) account
2. GitHub repository (already set up!)
3. GGUF model file (see below)

## Quick Deploy

### Option 1: Automatic Deploy (Recommended)

1. **The repo is already on GitHub!** Just connect it to Render.

2. Go to [dashboard.render.com](https://dashboard.render.com)

3. Click **"New +"** → **"Web Service"**

4. **Connect GitHub:**
   - Select repo: `revathi-stalin/deepseek-mcp`
   - Branch: `main`
   - Root directory: `server`

5. **Configure:**
   - **Name:** `deepseek-local-server`
   - **Runtime:** Docker
   - **Build Context:** `./server`
   - **Dockerfile:** `./server/Dockerfile`

6. **Environment Variables:**
   ```
   PORT = 8000
   MODEL_PATH = /app/models/deepseek-llama.gguf
   N_GPU_LAYERS = 0
   PYTHONUNBUFFERED = 1
   ```

7. **Add Disk Storage:**
   - Name: `model-storage`
   - Mount Path: `/app/models`
   - Size: 50 GB

8. **Deploy!**

### Option 2: Using render.yaml (One-Click)

The `render.yaml` file is already configured. Just:

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select your repo
4. Render will detect `render.yaml` automatically

## Upload Model to Render

Since models are large (4-8GB), you need to upload it separately:

### Method 1: Render Disk (Recommended)

1. After deployment, open your Render service
2. Go to **"Disks"** tab
3. Connect to your service via Render Shell:
   ```bash
   # In Render dashboard, click "Shell" button
   ```

4. Download model directly to the disk:
   ```bash
   cd /app/models
   curl -L -o deepseek-llama.gguf "https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF/resolve/main/deepseek-llama-7b-chat.Q4_K_M.gguf"
   ```

### Method 2: Render Shell Upload

1. Get the model locally:
   ```bash
   # On your machine
   python server/download_model.py --model deepseek-llama-7b-q4
   ```

2. Upload via Render Shell (using rsync or scp):
   ```bash
   # From your local machine
   rsync -avz --progress server/models/deepseek-llama.gguf \
       render@your-service.onrender.com:/app/models/
   ```

### Method 3: Render Deploy Script

Add this to your startup script:

```bash
# In Render Shell
cd /app/models
wget https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF/resolve/main/deepseek-llama-7b-chat.Q4_K_M.gguf \
     -O deepseek-llama.gguf
```

## Recommended Models

| Model | Size | RAM | Link |
|-------|------|-----|------|
| deepseek-llama-7b-q4 | 4.3GB | 8GB | [HuggingFace](https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF) |
| deepseek-coder-6.7b-q4 | 4.0GB | 8GB | [HuggingFace](https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF) |

## Test Your Deployed Server

```bash
# Health check
curl https://deepseek-local-server.onrender.com/health

# Test chat completion
curl -X POST https://deepseek-local-server.onrender.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 200
  }'

# Open web UI
# https://deepseek-local-server.onrender.com/web/
```

## Important Notes

⚠️ **CPU Only:** Render doesn't provide GPUs, so inference will be CPU-only (slower)

⚠️ **Service Limit:** The free tier has limited RAM. Use a Standard plan for 7B+ models

⚠️ **Cold Starts:** First request may be slow as the model loads into memory

⚠️ **Model Storage:** Use Render Disk to persist the model across deployments

## Performance Tips

1. **Use quantized models** (Q4 or Q5) for faster inference
2. **Increase context size** if needed: `--n-ctx 4096`
3. **Use Standard plan** for better CPU performance
4. **Keep service warm** to avoid cold starts

## Troubleshooting

**Out of memory:**
- Upgrade to Standard plan (more RAM)
- Use smaller model (7B instead of 33B)
- Reduce context size: `--n-ctx 1024`

**Slow inference:**
- Use Q4 quantized model
- Standard plan has faster CPUs
- Consider using a GPU provider instead

**Model not loading:**
- Check file path in environment variables
- Verify disk is mounted to `/app/models`
- Check file permissions in Render Shell

## Alternative: GPU-Based Deployment

For GPU inference, consider these platforms:
- **RunPod** - GPU cloud instances
- **Lambda Labs** - GPU servers
- **Vast.ai** - Cheap GPU rental
- **Modal** - Serverless GPU inference

Check `server/README.md` for local deployment instructions.
