import os

from inference_gateway import InferenceGatewayClient, Message

# Initialize client
client = InferenceGatewayClient("http://localhost:8080")

# Use environment variable with default model
LLM_NAME = os.getenv("LLM_NAME", "openai/gpt-4")

print(f"Using model: {LLM_NAME}")

# Simple chat completion
response = client.create_chat_completion(
    model=LLM_NAME,
    messages=[
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello!"),
    ],
)

print(response.choices[0].message.content)
