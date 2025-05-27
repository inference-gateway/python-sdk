# Examples

Before starting with the examples, ensure you have the inference-gateway up and running:

1. Copy the `.env.example` file to `.env` and set your provider key.

2. Run the Docker container:

```
docker run --rm -it -p 8080:8080 --env-file .env -e $LLM_NAME ghcr.io/inference-gateway/inference-gateway:latest
```

3. In a new terminal, set your preferred Large Language Model (LLM) provider for the examples:

```sh
export LLM_NAME=groq/meta-llama/llama-4-scout-17b-16e-instruct
```

And cd into the specific examples.

Recommended is to set the environment variable `ENVIRONMENT=development` in your `.env` file to enable debug mode.

The following examples demonstrate how to use the Inference Gateway SDK for various tasks:

- [List LLMs](list/README.md)
- [Chat](chat/README.md)
- [Tools](tools/README.md)
- [MCP](mcp/README.md)
