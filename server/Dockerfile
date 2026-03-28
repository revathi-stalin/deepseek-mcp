# DeepSeek Local AI Server - Dockerfile for Render
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install llama-cpp-python with CPU support
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=off" pip install --no-cache-dir llama-cpp-python

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY config.yaml .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create models directory and download model
RUN mkdir -p models && \
    cd models && \
    echo "Downloading DeepSeek model (this may take a while)..." && \
    curl -L -o deepseek-llama.gguf \
      "https://huggingface.co/TheBloke/deepseek-llama-7B-chat-GGUF/resolve/main/deepseek-llama-7b-chat.Q4_K_M.gguf" && \
    echo "Model downloaded successfully!" && \
    ls -lh deepseek-llama.gguf

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=models/deepseek-llama.gguf
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (downloads model if needed)
CMD ["./entrypoint.sh"]
