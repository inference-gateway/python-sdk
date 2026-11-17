import json
import os

from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


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
            # All chunks are SSEvent objects
            if chunk.data:
                try:
                    # Parse the raw JSON data
                    data = json.loads(chunk.data)
                except json.JSONDecodeError:
                    # Handle non-JSON SSE data
                    print(f"[Non-JSON chunk: {chunk.data}]", end="", flush=True)
                    continue

                for choice in data.get("choices", []):
                    content = choice.get("delta", {}).get("content")
                    if content:
                        print(content, end="", flush=True)

                    finish_reason = choice.get("finish_reason")
                    if finish_reason:
                        print(f"\n[Finished: {finish_reason}]")

        print("\n")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"\nStreaming Error: {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
