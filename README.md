# Inference Gateway Python SDK

An SDK written in Python for the [Inference Gateway](https://github.com/edenreich/inference-gateway).

- [Inference Gateway Python SDK](#inference-gateway-python-sdk)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Creating a Client](#creating-a-client)
    - [Listing Models](#listing-models)
    - [Generating Content](#generating-content)
  - [License](#license)

## Installation

```sh
pip install inference-gateway
```

## Usage

### Creating a Client

```python
from inference_gateway.client import InferenceGatewayClient


if __name__ == "__main__":
    client = InferenceGatewayClient("http://localhost:8080")

    models = client.list_models()
    print("Available models:", models)

    response = client.generate_content("providerName", "modelName", "your prompt here")
    print("Generated content:", response["Response"]["Content"])
```

### Listing Models

To list available models, use the list_models method:

```python
models = client.list_models()
print("Available models:", models)
```

### Generating Content

To generate content using a model, use the generate_content method:

```python
response = client.generate_content("providerName", "modelName", "your prompt here")
print("Generated content:", response["Response"]["Content"])
```

## License

This SDK is distributed under the MIT License, see [LICENSE](LICENSE) for more information.
