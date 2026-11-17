import json
import os

from inference_gateway import (
    InferenceGatewayClient,
    Response,
    ResponseFunctionToolCall,
    ResponseInputItem,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseTool,
)
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError
from inference_gateway.models import FunctionParameters

WEATHER_TOOL = ResponseTool(
    name="get_current_weather",
    description="Get the current weather in a given location",
    parameters=FunctionParameters(
        type="object",
        properties={
            "location": {"type": "string", "description": "The city, e.g. San Francisco"},
        },
        required=["location"],
    ),
)


def output_text(response: Response) -> str:
    """Join the text of every output message in a Responses API result."""
    return "".join(
        part.root.text
        for item in response.output
        if isinstance(item.root, ResponseOutputMessage)
        for part in item.root.content
        if isinstance(part.root, ResponseOutputText)
    )


def function_calls(response: Response) -> list[ResponseFunctionToolCall]:
    """Return the function tool calls the model requested in a Responses API result."""
    return [
        item.root for item in response.output if isinstance(item.root, ResponseFunctionToolCall)
    ]


def standard_response(client: InferenceGatewayClient, model: str) -> None:
    """Send a plain text prompt and print the generated text."""
    response = client.create_response(
        model=model,
        input="Hello! Please introduce yourself briefly.",
        max_output_tokens=100,
    )
    print(f"Response: {output_text(response)}")
    print(f"Status: {response.status.root}")


def streaming_response(client: InferenceGatewayClient, model: str) -> None:
    """Stream a response and print text deltas as typed ResponseStreamEvent objects arrive."""
    print("Assistant: ", end="", flush=True)
    for event in client.create_response_stream(
        model=model,
        input="Tell me a short story about a robot.",
        max_output_tokens=200,
    ):
        if event.type == "response.output_text.delta" and event.delta:
            print(event.delta, end="", flush=True)
        elif event.type == "response.completed":
            print("\n[Finished]")


def tool_call_response(client: InferenceGatewayClient, model: str) -> None:
    """Send a multi-turn input with a function tool and print any function calls returned."""
    response = client.create_response(
        model=model,
        input=[
            ResponseInputItem(role="system", content="You are a helpful weather assistant."),
            ResponseInputItem(role="user", content="Hi, I am planning a trip."),
            ResponseInputItem(role="assistant", content="Great! Where are you heading?"),
            ResponseInputItem(role="user", content="New York. What is the weather there?"),
        ],
        max_output_tokens=200,
        tools=[WEATHER_TOOL],
    )
    calls = function_calls(response)
    if not calls:
        print(f"No tool call. Response: {output_text(response)}")
    for call in calls:
        print(f"Tool called: {call.name} (call_id={call.call_id})")
        print(f"Arguments: {json.loads(call.arguments)}")


def main() -> None:
    """Demo standard, streaming and tool-calling requests to the OpenAI-compatible Responses API."""
    client = InferenceGatewayClient("http://localhost:8080/v1")
    model = os.getenv("LLM_NAME", "openai/gpt-4o")
    print(f"Using model: {model}")

    for title, demo in [
        ("Standard Response", standard_response),
        ("Streaming Response", streaming_response),
        ("Multi-Turn Input with a Function Tool", tool_call_response),
    ]:
        print(f"\n{title}:\n" + "-" * 30)
        try:
            demo(client, model)
        except (InferenceGatewayAPIError, InferenceGatewayError) as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
