# Decisions API Example

This example demonstrates the OpenAI Decisions API relay (`POST /v1/decisions`) using the Inference Gateway Python SDK. It shows how to:

- Ask one or more questions about a shared piece of evidence with `create_decision`
- Read the per-question answers from the response

**Prerequisites:** The Inference Gateway must be configured with a provider that supports the Decisions API (currently OpenAI) and its API key set in the `.env` file. Other providers return `400` with `The Decisions API is not supported by this provider yet.`

## Usage

1. **Set up environment**:

   ```bash
   export DECISION_MODEL="openai/gpt-6-luna"
   ```

2. **Run the example**:

   ```bash
   python main.py
   ```

## Code Example

```python
from inference_gateway import InferenceGatewayClient

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_decision(
    model="openai/gpt-6-luna",
    input="Buy now!!!",
    questions=[
        {
            "type": "predicate",
            "name": "is_spam",
            "instructions": "Is this message unsolicited marketing spam?",
        }
    ],
)

for answer in response.answers or []:
    print(answer["name"], answer["value"])
```

`input` is either a string or an ordered list of message and tool items. Questions are `predicate`, `choice` (with `choices`) or `score` (with 2-10 `levels`).

## Configuration

The example uses these environment variables:

- `DECISION_MODEL`: The model used for decisions (default: `openai/gpt-6-luna`)
