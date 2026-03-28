"""
DeepSeek Local AI Server
Run DeepSeek models locally on your own hardware
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")


class Message(BaseModel):
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    model: str = Field("deepseek-llama", description="Model identifier")
    messages: List[Message] = Field(..., description="Conversation messages")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Maximum tokens to generate")
    top_p: float = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling threshold")
    top_k: int = Field(40, ge=1, description="Top-k sampling parameter")
    stream: bool = Field(False, description="Enable streaming")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "local"
    permission: List = []


class DeepSeekServer:
    """Local DeepSeek AI Server"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("MODEL_PATH", "models/deepseek-llama.gguf")
        self.model = None
        self.app = FastAPI(
            title="DeepSeek Local AI Server",
            description="Local AI server running DeepSeek models",
            version="1.0.0"
        )
        self._setup_middleware()
        self._setup_routes()
        self._setup_static_files()

    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "name": "DeepSeek Local AI Server",
                "version": "1.0.0",
                "status": "running",
                "model_loaded": self.model is not None,
                "endpoints": {
                    "models": "/v1/models",
                    "chat": "/v1/chat/completions",
                    "health": "/health"
                }
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "model_loaded": self.model is not None,
                "model_path": self.model_path
            }

        @self.app.get("/v1/models")
        async def list_models():
            return {
                "object": "list",
                "data": [
                    {
                        "id": "deepseek-llama",
                        "object": "model",
                        "owned_by": "local",
                        "permission": []
                    }
                ]
            }

        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """Generate chat completions"""
            if not LLAMA_CPP_AVAILABLE:
                raise HTTPException(
                    status_code=501,
                    detail="llama-cpp-python not installed. Install with: pip install llama-cpp-python"
                )

            if self.model is None:
                raise HTTPException(
                    status_code=503,
                    detail="Model not loaded. Please load a model first."
                )

            try:
                # Format messages into prompt
                prompt = self._format_messages(request.messages)

                # Generate completion
                response = self.model(
                    prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    stop=request.stop if request.stop else None,
                    echo=False
                )

                # Extract generated text
                generated_text = response['choices'][0]['text'].strip()

                return ChatCompletionResponse(
                    id=f"chatcmpl-{asyncio.get_event_loop().time()}",
                    created=int(asyncio.get_event_loop().time()),
                    model=request.model,
                    choices=[{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": generated_text
                        },
                        "finish_reason": "stop"
                    }],
                    usage={
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(generated_text.split()),
                        "total_tokens": len(prompt.split()) + len(generated_text.split())
                    }
                )

            except Exception as e:
                logger.error(f"Error generating completion: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _setup_static_files(self):
        """Setup static file serving for web UI"""
        web_path = Path(__file__).parent / "web"
        if web_path.exists():
            self.app.mount("/web", StaticFiles(directory=str(web_path), html=True), name="web")

            @self.app.get("/web")
            async def web_ui():
                return FileResponse(web_path / "index.html")

    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages into a prompt for the model"""
        prompt = ""
        for msg in messages:
            if msg.role == "system":
                prompt += f"<|system|>\n{msg.content}\n"
            elif msg.role == "user":
                prompt += f"<|user|>\n{msg.content}\n"
            elif msg.role == "assistant":
                prompt += f"<|assistant|>\n{msg.content}\n"

        prompt += "<|assistant|>\n"
        return prompt

    def load_model(self, model_path: Optional[str] = None, n_ctx: int = 2048, n_gpu_layers: int = -1):
        """Load a model from disk"""
        if not LLAMA_CPP_AVAILABLE:
            raise RuntimeError("llama-cpp-python not installed")

        model_path = model_path or self.model_path

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        logger.info(f"Loading model from: {model_path}")

        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )

        logger.info("Model loaded successfully!")
        return self.model

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server"""
        logger.info(f"Starting DeepSeek Local AI Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek Local AI Server")
    parser.add_argument("--model", type=str, help="Path to model file (.gguf format)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--n-ctx", type=int, default=2048, help="Context size")
    parser.add_argument("--n-gpu-layers", type=int, default=-1, help="Number of GPU layers (-1 for all)")

    args = parser.parse_args()

    # Create server
    server = DeepSeekServer(model_path=args.model)

    # Load model if path provided
    if args.model or os.getenv("MODEL_PATH"):
        try:
            server.load_model(
                model_path=args.model or os.getenv("MODEL_PATH"),
                n_ctx=args.n_ctx,
                n_gpu_layers=args.n_gpu_layers
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.info("Server will start without a model loaded")

    # Run server
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
