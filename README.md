# Inference Gateway Python SDK

An SDK written in Python for the [Inference Gateway](https://github.com/edenreich/inference-gateway).

- [Inference Gateway Python SDK](#inference-gateway-python-sdk)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Creating a Client](#creating-a-client)
    - [Listing Models](#listing-models)
    - [List Provider's Models](#list-providers-models)
    - [Generating Content](#generating-content)
    - [Streaming Content](#streaming-content)
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

To list all available models from all providers, use the list_models method:

```python
models = client.list_models()
print("Available models: ", models)
```

### List Provider's Models

To list available models for a specific provider, use the list_provider_models method:

```python
models = client.list_provider_models(Provider.OPENAI)
print("Available OpenAI models: ", models)
```

### Generating Content

To generate content using a model, use the generate_content method:

```python
from inference_gateway.client import Provider, Role, Message

messages = [
    Message(
      Role.SYSTEM, 
      "You are an helpful assistant"
    ),
    Message(
      Role.USER, 
      "Hello!"
    ),
]

response = client.generate_content(
    provider=Provider.OPENAI,
    model="gpt-4",
    messages=messages
)
print("Assistant: ", response["response"]["content"])
```

### Streaming Content

To stream content using a model, use the stream_content method:

```python
from inference_gateway.client import Provider, Role, Message

messages = [
    Message(
      Role.SYSTEM, 
      "You are an helpful assistant"
    ),
    Message(
      Role.USER, 
      "Hello!"
    ),
]

# Use SSE for streaming
for response in client.generate_content_stream(
    provider=Provider.Ollama,
    model="llama2",
    messages=messages,
    use_sse=true
):
print("Event: ", response["event"])
print("Assistant: ", response["data"]["content"])

# Or raw JSON response
for response in client.generate_content_stream(
    provider=Provider.GROQ,
    model="deepseek-r1",
    messages=messages,
    use_sse=false
):
print("Assistant: ", response.content)
```

### Health Check

To check the health of the API, use the health_check method:

```python
is_healthy = client.health_check()
print("API Status: ", "Healthy" if is_healthy else "Unhealthy")
```

## License

This SDK is distributed under the MIT License, see [LICENSE](LICENSE) for more information.
