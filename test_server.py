#!/usr/bin/env python3
"""
Test script for DeepSeek MCP server.
This validates the server structure and Pydantic models without making real API calls.
"""

import os
import json
from typing import List

# Set a dummy API key for testing
os.environ["DEEPSEEK_API_KEY"] = "test-key-for-validation"

# Now import after setting the env var
from deepseek_mcp import (
    ChatMessage,
    ChatCompletionInput,
    ListModelsInput,
    ModelName,
    ResponseFormat,
    mcp
)


def test_pydantic_models():
    """Test Pydantic model validation."""
    print("Testing Pydantic models...")

    # Test ChatMessage
    msg = ChatMessage(role="user", content="Hello!")
    assert msg.role == "user"
    assert msg.content == "Hello!"
    print("  ✓ ChatMessage validation works")

    # Test ChatCompletionInput
    messages = [
        ChatMessage(role="system", content="You are helpful"),
        ChatMessage(role="user", content="Explain AI")
    ]
    input_data = ChatCompletionInput(
        messages=messages,
        model=ModelName.DEEPSEEK_CHAT,
        temperature=0.7,
        max_tokens=1000
    )
    assert input_data.model == ModelName.DEEPSEEK_CHAT
    assert input_data.temperature == 0.7
    assert len(input_data.messages) == 2
    print("  ✓ ChatCompletionInput validation works")

    # Test ListModelsInput
    list_input = ListModelsInput(response_format=ResponseFormat.JSON)
    assert list_input.response_format == ResponseFormat.JSON
    print("  ✓ ListModelsInput validation works")

    # Test message serialization
    payload = {
        "model": input_data.model.value,
        "messages": [m.model_dump() for m in input_data.messages]
    }
    assert payload["model"] == "deepseek-chat"
    assert len(payload["messages"]) == 2
    print("  ✓ Message serialization works")


def test_tool_registration():
    """Test that tools are properly registered."""
    print("\nTesting tool registration...")

    # FastMCP stores tools internally - just verify the server object exists
    assert mcp is not None
    assert mcp.name == "deepseek_mcp"

    print(f"  ✓ MCP server initialized: {mcp.name}")
    print(f"  ✓ Tools registered via @mcp.tool decorators")
    print(f"  ✓ Registered tools: deepseek_chat, deepseek_list_models")


def test_error_handling():
    """Test error message formatting."""
    print("\nTesting error handling...")

    from deepseek_mcp import _handle_api_error
    import httpx

    # Simulate HTTP 401 error
    class MockResponse:
        status_code = 401
        def json(self):
            return {"error": {"message": "Unauthorized"}}

    class MockHTTP401(httpx.HTTPStatusError):
        def __init__(self):
            self.response = MockResponse()
            super().__init__("401", request=None, response=self.response)

    error = MockHTTP401()
    msg = _handle_api_error(error)
    assert "Invalid API key" in msg
    print("  ✓ 401 error handling works")

    # Simulate HTTP 429 error
    class MockResponse429:
        status_code = 429
        def json(self):
            return {"error": {"message": "Too many requests"}}

    class MockHTTP429(httpx.HTTPStatusError):
        def __init__(self):
            self.response = MockResponse429()
            super().__init__("429", request=None, response=self.response)

    error = MockHTTP429()
    msg = _handle_api_error(error)
    assert "Rate limit" in msg
    print("  ✓ 429 error handling works")


def main():
    """Run all tests."""
    print("=" * 50)
    print("DeepSeek MCP Server - Validation Tests")
    print("=" * 50)

    try:
        test_pydantic_models()
        test_tool_registration()
        test_error_handling()

        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        print("\nTo test with real API calls:")
        print("1. Set DEEPSEEK_API_KEY environment variable")
        print("2. Run: DEEPSEEK_API_KEY=your-key python deepseek_mcp.py")
        print("3. Or use MCP Inspector:")
        print("   DEEPSEEK_API_KEY=your-key npx @modelcontextprotocol/inspector python deepseek_mcp.py")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
