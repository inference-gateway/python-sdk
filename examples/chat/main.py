import json
import os

from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError
from inference_gateway.models import SSEvent


def main() -> None:
    """
    Simple demo of standard and streaming chat completions using the Inference Gateway Python SDK.
    """
    # Initialize client
    client = InferenceGatewayClient("http://localhost:8080/v1")

    # Use environment variable with default model
    LLM_NAME = os.getenv("LLM_NAME", "openai/gpt-4")
    print(f"Using model: {LLM_NAME}")
    print("=" * 50)

    # Example 1: Standard Chat Completion
    print("\n1. Standard Chat Completion:")
    print("-" * 30)

    try:
        response = client.create_chat_completion(
            model=LLM_NAME,
            messages=[
                Message(role="system", content="You are a helpful assistant"),
                Message(role="user", content="Hello! Please introduce yourself briefly."),
            ],
            max_tokens=100,
        )

        print(f"Response: {response.choices[0].message.content}")
        if response.usage:
            print(f"Usage: {response.usage.total_tokens} tokens")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")
        return

    # Example 2: Streaming Chat Completion
    print("\n\n2. Streaming Chat Completion:")
    print("-" * 30)

    try:
        print("Assistant: ", end="", flush=True)

        stream = client.create_chat_completion_stream(
            model=LLM_NAME,
            messages=[
                Message(role="system", content="You are a helpful assistant"),
                Message(role="user", content="Tell me a short story about a robot."),
            ],
            max_tokens=200,
        )

        for chunk in stream:
            if isinstance(chunk, SSEvent):
                # Handle Server-Sent Events format
                if chunk.data:
                    try:
                        data = json.loads(chunk.data)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                print(delta["content"], end="", flush=True)
                    except json.JSONDecodeError:
                        pass
            elif isinstance(chunk, dict):
                # Handle JSON format
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        print(delta["content"], end="", flush=True)

        print("\n")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"\nStreaming Error: {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
