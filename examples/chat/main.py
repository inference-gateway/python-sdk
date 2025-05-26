import json
import os

from pydantic import ValidationError

from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError
from inference_gateway.models import CreateChatCompletionStreamResponse, SSEvent


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
            # All chunks are now SSEvent objects
            if chunk.data:
                try:
                    # Parse the raw JSON data
                    data = json.loads(chunk.data)

                    # Try to unmarshal to structured model for type safety
                    try:
                        structured_chunk = CreateChatCompletionStreamResponse.model_validate(data)

                        # Use the structured model for better type safety and IDE support
                        if structured_chunk.choices and len(structured_chunk.choices) > 0:
                            choice = structured_chunk.choices[0]
                            if hasattr(choice.delta, "content") and choice.delta.content:
                                print(choice.delta.content, end="", flush=True)

                            # Optionally show other information
                            if choice.finish_reason and choice.finish_reason != "null":
                                print(f"\n[Finished: {choice.finish_reason}]")

                    except ValidationError:
                        # Fallback to manual parsing for non-standard chunks
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                print(delta["content"], end="", flush=True)

                except json.JSONDecodeError:
                    # Handle non-JSON SSE data
                    print(f"[Non-JSON chunk: {chunk.data}]", end="", flush=True)

        print("\n")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"\nStreaming Error: {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
