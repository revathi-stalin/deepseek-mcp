"""
DeepSeek Model Inference API
FastAPI server for serving fine-tuned DeepSeek models on Render
"""

import os
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
tokenizer = None


class Message(BaseModel):
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="Conversation messages")
    model: Optional[str] = Field("deepseek-v3-finetuned", description="Model identifier")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(512, ge=1, le=4096, description="Maximum tokens to generate")
    top_p: float = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling threshold")
    stream: bool = Field(False, description="Enable streaming responses")


class ChatResponse(BaseModel):
    content: str = Field(..., description="Generated response content")
    model: str = Field(..., description="Model used")
    finish_reason: str = Field("stop", description="Reason for completion")


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    global model, tokenizer

    # Model paths from environment
    base_model_path = os.getenv("BASE_MODEL_PATH", "deepseek-ai/DeepSeek-V3")
    lora_path = os.getenv("LORA_PATH", "/app/models/lora")

    logger.info(f"Loading base model from: {base_model_path}")
    logger.info(f"Loading LoRA adapters from: {lora_path}")

    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            trust_remote_code=True
        )
        tokenizer.pad_token = tokenizer.eos_token

        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        # Load LoRA adapters if available
        if os.path.exists(lora_path):
            logger.info("Loading LoRA adapters...")
            model = PeftModel.from_pretrained(base_model, lora_path)
            model = model.merge_and_unload()
        else:
            logger.warning("LoRA path not found, using base model")
            model = base_model

        model.eval()
        logger.info("Model loaded successfully!")

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = None
        tokenizer = None

    yield

    # Cleanup
    logger.info("Shutting down...")
    del model
    del tokenizer
    torch.cuda.empty_cache()


# Initialize FastAPI
app = FastAPI(
    title="DeepSeek Model Inference API",
    description="API for serving fine-tuned DeepSeek models",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "DeepSeek Model Inference API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/v1/chat/completions",
            "models": "/v1/models"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_name=os.getenv("BASE_MODEL_PATH", "deepseek-ai/DeepSeek-V3")
    )


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    """Generate chat completions using the fine-tuned model"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Format messages into prompt
        prompt = format_messages(request.messages)

        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(model.device)

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.temperature > 0,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decode response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the new response
        response_text = extract_response(response_text, prompt)

        return ChatResponse(
            content=response_text,
            model=request.model,
            finish_reason="stop"
        )

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {
                "id": "deepseek-v3-finetuned",
                "object": "model",
                "owned_by": "custom",
                "permission": []
            }
        ]
    }


def format_messages(messages: List[Message]) -> str:
    """Format messages into a prompt for the model"""
    formatted = ""
    for msg in messages:
        if msg.role == "system":
            formatted += f"### System:\n{msg.content}\n\n"
        elif msg.role == "user":
            formatted += f"### User:\n{msg.content}\n\n"
        elif msg.role == "assistant":
            formatted += f"### Assistant:\n{msg.content}\n\n"

    formatted += "### Assistant:\n"
    return formatted


def extract_response(full_response: str, prompt: str) -> str:
    """Extract only the new response from the generated text"""
    if prompt in full_response:
        return full_response[len(prompt):].strip()
    return full_response.strip()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
