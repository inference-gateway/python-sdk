# List LLMs Example

This example demonstrates how to use the Inference Gateway Python SDK to list available language models. It shows how to:

- Connect to the Inference Gateway
- List all available models
- Filter models by provider (e.g., OpenAI, Groq, etc.)

Run the example with:

```bash
python main.py
```

You can specify a different model provider by setting the `LLM_NAME` environment variable:

```bash
LLM_NAME=openai/gpt-4 python main.py
```
