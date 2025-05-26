import os

from inference_gateway import InferenceGatewayClient

# Initialize client
client = InferenceGatewayClient("http://localhost:8080/v1")

# Use environment variable with default model
LLM_NAME = os.getenv("LLM_NAME", "groq/llama3-8b-8192")

PROVIDER = LLM_NAME.split("/")[0]

print(f"Using provider: {PROVIDER}")

# List all available models
models = client.list_models()
print("All models:", models)

# Filter by provider
openai_models = client.list_models(provider=PROVIDER)
print("Provider {PROVIDER} models:", openai_models)
