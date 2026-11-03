import os

from inference_gateway import InferenceGatewayClient
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


def main() -> None:
    """
    Simple demo of the OpenAI Decisions API relay
    using the Inference Gateway Python SDK.
    """
    client = InferenceGatewayClient("http://localhost:8080/v1")

    MODEL = os.getenv("DECISION_MODEL", "openai/gpt-6-luna")
    print(f"Using model: {MODEL}")
    print("=" * 50)

    try:
        response = client.create_decision(
            model=MODEL,
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
            print(f"{answer.get('name')}: {answer.get('value')}")

        if response.usage:
            print(f"Usage: {response.usage.input_tokens} input tokens")

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
