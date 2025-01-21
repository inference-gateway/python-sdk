# Inference Gateway Python SDK

An SDK written in Python for the [Inference Gateway](https://github.com/edenreich/inference-gateway).

- [Inference Gateway Python SDK](#inference-gateway-python-sdk)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Creating a Client](#creating-a-client)
    - [Listing Models](#listing-models)
    - [Generating Content](#generating-content)
    - [Health Check](#health-check)
  - [License](#license)

## Installation

```sh
pip install inference-gateway
```

## Usage

### Creating a Client

```python
from inference_gateway.client import InferenceGatewayClient, Provider

client = InferenceGatewayClient("http://localhost:8080")

# With authentication token(optional)
client = InferenceGatewayClient("http://localhost:8080", token="your-token")
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
from inference_gateway.client import Provider, Role, Message

messages = [
    Message(Role.SYSTEM, "You are a helpful assistant"),
    Message(Role.USER, "Hello!"),
]

response = client.generate_content(
    provider=Provider.OPENAI,
    model="gpt-4",
    messages=messages
)
print("Assistant:", response["choices"][0]["message"]["content"])
```

### Health Check

To check the health of the API, use the health_check method:

```python
is_healthy = client.health_check()
print("API Status:", "Healthy" if is_healthy else "Unhealthy")
```

## License

This SDK is distributed under the MIT License, see [LICENSE](LICENSE) for more information.
