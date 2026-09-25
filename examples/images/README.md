# Images API Example

This example demonstrates image generation and editing via the OpenAI-compatible Images API using the Inference Gateway Python SDK. It shows how to:

- Generate an image from a text prompt with `create_image`
- Edit an existing image with `create_image_edit` (optional)

**Prerequisites:** The Inference Gateway must be configured with an image-capable provider (for example OpenAI) and its API key set in the `.env` file.

## Usage

1. **Set up environment**:

   ```bash
   export IMAGE_MODEL="openai/dall-e-3"
   ```

2. **Run the example**:

   ```bash
   python main.py
   ```

3. **Optional - demo image edits**: edits (`POST /images/edits`) need a source image file:

   ```bash
   export INPUT_IMAGE=/path/to/image.png
   ```

## Code Examples

### Image Generation

```python
from inference_gateway import InferenceGatewayClient

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_image(
    prompt="A friendly robot painting a sunset, digital art",
    model="openai/dall-e-3",
    provider="openai",
    n=1,
    size="1024x1024",
)

for image in response.data:
    print(image.url)
    if image.revised_prompt:
        print("Revised prompt:", image.revised_prompt)
```

### Image Edit

```python
with open("/path/to/image.png", "rb") as f:
    edited = client.create_image_edit(
        image=("image.png", f),
        prompt="Add a rainbow in the background",
        model="openai/dall-e-3",
        provider="openai",
        size="1024x1024",
    )

print(edited.data[0].url)
```

## Configuration

The example uses these environment variables:

- `IMAGE_MODEL`: The model used for generation and edits (default: `openai/dall-e-3`)
- `INPUT_IMAGE`: Optional path to a PNG used to demo `create_image_edit`