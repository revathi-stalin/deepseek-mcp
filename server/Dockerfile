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
COPY entrypoint-fixed.sh .

# Make entrypoint executable
RUN chmod +x entrypoint-fixed.sh

# Copy web UI
RUN mkdir -p /app/web
COPY web/ /app/web/ 2>/dev/null || true

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=models/deepseek-llama.gguf
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (downloads model on startup)
CMD ["./entrypoint-fixed.sh"]
