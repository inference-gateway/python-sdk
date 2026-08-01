import os

from inference_gateway import InferenceGatewayClient
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


def main() -> None:
    """
    Simple demo of image generation, edits, and variations via the
    OpenAI-compatible Images API using the Inference Gateway Python SDK.
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

        # Image edits and variations (POST /images/edits, /images/variations)
        # need a source image file - set INPUT_IMAGE to try them.
        input_image = os.getenv("INPUT_IMAGE")
        if input_image:
            with open(input_image, "rb") as f:
                edited = client.create_image_edit(
                    image=("image.png", f),
                    prompt="Add a rainbow in the background",
                    model=MODEL,
                    provider="openai",
                    size="1024x1024",
                )
            print(f"Edited image: {edited.data[0].url or '[base64 data]'}")

            with open(input_image, "rb") as f:
                variation = client.create_image_variation(
                    image=("image.png", f),
                    model=MODEL,
                    provider="openai",
                    n=1,
                    size="1024x1024",
                )
            print(f"Variation: {variation.data[0].url or '[base64 data]'}")
        else:
            print("Set INPUT_IMAGE=/path/to/image.png to demo edits and variations")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
