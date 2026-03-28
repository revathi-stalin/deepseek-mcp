"""
Test script for DeepSeek Inference API
Run this after deploying to Render to test the API
"""

import requests
import json


def test_api(base_url="http://localhost:8000"):
    """Test the inference API endpoints"""

    print("Testing DeepSeek Inference API")
    print("=" * 50)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: List models
    print("\n3. Testing models endpoint...")
    response = requests.get(f"{base_url}/v1/models")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Chat completion
    print("\n4. Testing chat completion...")
    chat_request = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=chat_request,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Model: {result['model']}")
        print(f"   Response: {result['content'][:200]}...")
    else:
        print(f"   Error: {response.text}")

    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    import sys

    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing API at: {base_url}\n")
    test_api(base_url)
