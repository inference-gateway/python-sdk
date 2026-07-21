import os

from inference_gateway import InferenceGatewayClient, MessagesMessage, MessagesTextBlock
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


def main() -> None:
    """
    Simple demo of standard and streaming requests to the Anthropic-compatible
    Messages API using the Inference Gateway Python SDK.
    """
    # Initialize client
    client = InferenceGatewayClient("http://localhost:8080/v1")

    # Use environment variable with default model
    LLM_NAME = os.getenv("LLM_NAME", "anthropic/claude-sonnet-5")
    print(f"Using model: {LLM_NAME}")
    print("=" * 50)

    # Example 1: Standard Message
    print("\n1. Standard Message:")
    print("-" * 30)

    try:
        response = client.create_message(
            model=LLM_NAME,
            messages=[
                MessagesMessage(role="user", content="Hello! Please introduce yourself briefly."),
            ],
            max_tokens=100,
            system="You are a helpful assistant",
        )

        for block in response.content:
            if isinstance(block.root, MessagesTextBlock):
                print(f"Response: {block.root.text}")
        print(f"Stop reason: {response.stop_reason}")
        print(f"Usage: {response.usage.input_tokens} in / {response.usage.output_tokens} out")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")
        return

    # Example 2: Streaming Message
    print("\n\n2. Streaming Message:")
    print("-" * 30)

    try:
        print("Assistant: ", end="", flush=True)

        stream = client.create_message_stream(
            model=LLM_NAME,
            messages=[
                MessagesMessage(role="user", content="Tell me a short story about a robot."),
            ],
            max_tokens=200,
            system="You are a helpful assistant",
        )

        for event in stream:
            # Events are typed MessagesStreamEvent objects
            if event.type == "content_block_delta" and event.delta and event.delta.text:
                print(event.delta.text, end="", flush=True)
            elif event.type == "message_delta" and event.delta and event.delta.stop_reason:
                print(f"\n[Finished: {event.delta.stop_reason}]")

        print("\n")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"\nStreaming Error: {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
