#!/usr/bin/env python3
"""
DeepSeek MCP Server.

This server provides Model Context Protocol tools to interact with DeepSeek AI models.
It exposes chat completion and model listing capabilities through an OpenAI-compatible API.

Environment Variables:
    DEEPSEEK_API_KEY: Your DeepSeek API key (required)

Usage:
    # Local testing with MCP Inspector
    DEEPSEEK_API_KEY=your-key python deepseek_mcp.py

    # Run with streamable HTTP transport
    DEEPSEEK_API_KEY=your-key python deepseek_mcp.py --transport streamable_http --port 8000
"""

from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import os
import json
import asyncio
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("deepseek_mcp")

# Constants
API_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError(
        "DEEPSEEK_API_KEY environment variable is required. "
        "Get your API key from https://platform.deepseek.com/"
    )


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class ModelName(str, Enum):
    """Available DeepSeek models."""
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"


# Pydantic Models for Input Validation
class ChatMessage(BaseModel):
    """A chat message in the conversation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="The role of the message author"
    )
    content: str = Field(
        ...,
        description="The message content",
        min_length=1,
        max_length=100000
    )


class ChatCompletionInput(BaseModel):
    """Input model for chat completion requests."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    messages: List[ChatMessage] = Field(
        ...,
        description="List of messages in the conversation",
        min_length=1,
        max_length=200
    )
    model: ModelName = Field(
        default=ModelName.DEEPSEEK_CHAT,
        description="The model to use for completion"
    )
    temperature: Optional[float] = Field(
        default=1.0,
        description="Sampling temperature (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to generate",
        ge=1,
        le=8192
    )
    top_p: Optional[float] = Field(
        default=1.0,
        description="Nucleus sampling parameter (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    stream: Optional[bool] = Field(
        default=False,
        description="Whether to stream the response"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format: 'json' or 'markdown'"
    )

    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        """Validate message sequence."""
        if not v:
            raise ValueError("Messages list cannot be empty")
        # Check that messages start with user or system
        if v[0].role not in ["user", "system"]:
            raise ValueError("First message must be from 'user' or 'system' role")
        return v


class ListModelsInput(BaseModel):
    """Input model for listing available models."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format: 'json' or 'markdown'"
    )


# Shared utility functions
async def _make_api_request(
    endpoint: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Reusable function for all API calls."""
    default_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            headers=default_headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            error_data = e.response.json()
            error_msg = error_data.get("error", {}).get("message", "")
        except Exception:
            error_msg = ""

        if status == 401:
            return "Error: Invalid API key. Please check your DEEPSEEK_API_KEY environment variable."
        elif status == 404:
            return "Error: Resource not found. Please check the model name."
        elif status == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        elif status == 400:
            return f"Error: Bad request. {error_msg}"
        return f"Error: API request failed with status {status}. {error_msg}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"


def _format_chat_markdown(response: Dict[str, Any], model: str) -> str:
    """Format chat completion response as Markdown."""
    lines = ["# DeepSeek Chat Completion\n", f"**Model**: {model}\n"]

    if "choices" in response and response["choices"]:
        choice = response["choices"][0]
        message = choice.get("message", {})
        content = message.get("content", "")

        lines.append(f"**Role**: {message.get('role', 'assistant')}\n")
        lines.append(f"**Finish Reason**: {choice.get('finish_reason', 'unknown')}\n")

        if "usage" in response:
            usage = response["usage"]
            lines.append("\n### Token Usage")
            lines.append(f"- **Prompt Tokens**: {usage.get('prompt_tokens', 0)}")
            lines.append(f"- **Completion Tokens**: {usage.get('completion_tokens', 0)}")
            lines.append(f"- **Total Tokens**: {usage.get('total_tokens', 0)}")

        lines.append("\n### Response")
        lines.append(content)

    return "\n".join(lines)


# Tool definitions
@mcp.tool(
    name="deepseek_chat",
    annotations={
        "title": "DeepSeek Chat Completion",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def deepseek_chat(params: ChatCompletionInput) -> str:
    """
    Generate chat completions using DeepSeek AI models.

    This tool sends a conversation to DeepSeek's AI models and returns the model's response.
    It supports both system messages and multi-turn conversations.

    Args:
        params (ChatCompletionInput): Validated input parameters containing:
            - messages (List[ChatMessage]): Conversation messages with role and content
            - model (ModelName): Model to use (default: deepseek-chat)
            - temperature (Optional[float]): Sampling temperature 0.0-2.0 (default: 1.0)
            - max_tokens (Optional[int]): Maximum tokens to generate (default: None)
            - top_p (Optional[float]): Nucleus sampling 0.0-1.0 (default: 1.0)
            - stream (Optional[bool]): Whether to stream response (default: False)
            - response_format (ResponseFormat): Output format (default: JSON)

    Returns:
        str: JSON or Markdown formatted response containing:
            - id (str): Response identifier
            - choices (List[Dict]): Generated message choices
            - usage (Dict): Token usage statistics
            - model (str): Model used

    Success response (JSON):
        {
            "id": "chat-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Response text here"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

    Error response:
        "Error: <error message>"

    Examples:
        - Simple chat: messages=[{"role": "user", "content": "Hello!"}]
        - With system prompt: messages=[{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "Explain AI"}]
        - Multi-turn: messages=[{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}, {"role": "user", "content": "How are you?"}]

    Error Handling:
        - 401: Invalid API key
        - 429: Rate limit exceeded
        - 400: Invalid request parameters
    """
    try:
        # Build request payload
        payload = {
            "model": params.model.value,
            "messages": [m.model_dump() for m in params.messages],
            "temperature": params.temperature,
            "top_p": params.top_p,
            "stream": params.stream
        }
        if params.max_tokens is not None:
            payload["max_tokens"] = params.max_tokens

        # Make API request
        response = await _make_api_request(
            "chat/completions",
            method="POST",
            json=payload
        )

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_chat_markdown(response, params.model.value)
        else:
            return json.dumps(response, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="deepseek_list_models",
    annotations={
        "title": "List DeepSeek Models",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def deepseek_list_models(params: ListModelsInput) -> str:
    """
    List available DeepSeek AI models.

    This tool returns information about available DeepSeek models that can be used
    with the deepseek_chat tool.

    Args:
        params (ListModelsInput): Validated input parameters containing:
            - response_format (ResponseFormat): Output format (default: JSON)

    Returns:
        str: JSON or Markdown formatted response containing available models.

    Success response (JSON):
        {
            "object": "list",
            "data": [
                {
                    "id": "deepseek-chat",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "deepseek"
                },
                {
                    "id": "deepseek-coder",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "deepseek"
                }
            ]
        }

    Error response:
        "Error: <error message>"

    Examples:
        - List all models: Call with default parameters
        - Get markdown format: response_format="markdown"

    Error Handling:
        - 401: Invalid API key
        - Network errors: Connection issues
    """
    try:
        response = await _make_api_request("models", method="GET")

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# DeepSeek Available Models\n"]
            for model in response.get("data", []):
                lines.append(f"## {model.get('id', 'unknown')}")
                lines.append(f"- **Object**: {model.get('object', 'model')}")
                lines.append(f"- **Owned by**: {model.get('owned_by', 'deepseek')}")
                lines.append("")
            return "\n".join(lines)
        else:
            return json.dumps(response, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    # Run the MCP server
    import sys

    # Check for transport arguments
    transport = "stdio"
    port = 8000

    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    if transport == "streamable_http":
        mcp.run(transport="streamable_http", port=port)
    else:
        mcp.run()
