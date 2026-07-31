import os

from inference_gateway import InferenceGatewayClient
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


def main() -> None:
    """
    Simple demo of image generation via the OpenAI-compatible Images API
    (POST /images/generations) using the Inference Gateway Python SDK.
    """
    client = InferenceGatewayClient("http://localhost:8080/v1")

    MODEL = os.getenv("IMAGE_MODEL", "openai/dall-e-3")
    print(f"Using model: {MODEL}")
    print("=" * 50)

    try:
        response = client.create_image(
            prompt="A friendly robot painting a sunset, digital art",
            model=MODEL,
            provider="openai",
            n=1,
            size="1024x1024",
        )

        for i, image in enumerate(response.data, start=1):
            print(f"Image {i}: {image.url or '[base64 data]'}")
            if image.revised_prompt:
                print(f"  Revised prompt: {image.revised_prompt}")

        if response.usage:
            print(f"Usage: {response.usage.total_tokens} total tokens")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
