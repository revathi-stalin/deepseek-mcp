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
