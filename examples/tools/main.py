#!/usr/bin/env python3
"""
Example demonstrating tool use with the Inference Gateway Python SDK.

This example shows how to:
1. Define tools/functions using type-safe Pydantic models
2. Make chat completions with tool calling enabled
3. Handle tool calls from the model
4. Simulate tool execution and continue the conversation
"""

import json
import os
from typing import Any, Dict

from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.models import (
    ChatCompletionMessageToolCall,
    ChatCompletionTool,
    FunctionObject,
    FunctionParameters,
)

# Initialize client
client = InferenceGatewayClient("http://localhost:8080/v1")

# Use environment variable with default model
LLM_NAME = os.getenv("LLM_NAME", "openai/gpt-4")

print(f"Using model: {LLM_NAME}")

# Define weather tool using type-safe Pydantic models
weather_tool = ChatCompletionTool(
    type="function",
    function=FunctionObject(
        name="get_current_weather",
        description="Get the current weather in a given location",
        parameters=FunctionParameters(
            type="object",
            properties={
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use",
                },
            },
            required=["location"],
        ),
    ),
)

# Define calculator tool using type-safe Pydantic models
calculator_tool = ChatCompletionTool(
    type="function",
    function=FunctionObject(
        name="calculate",
        description="Perform basic mathematical calculations",
        parameters=FunctionParameters(
            type="object",
            properties={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate, e.g. '2 + 3 * 4'",
                }
            },
            required=["expression"],
        ),
    ),
)


def simulate_weather_api(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """Simulate a weather API call."""
    # This would normally call a real weather API
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "partly cloudy",
        "humidity": 65,
        "wind_speed": 10,
    }
    return weather_data


def simulate_calculator(expression: str) -> Dict[str, Any]:
    """Simulate a calculator function."""
    try:
        # Safe evaluation of mathematical expressions
        # In production, use a proper math parser instead of eval
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


def execute_tool_call(tool_call: ChatCompletionMessageToolCall) -> str:
    """Execute a tool call and return the result as a JSON string."""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "get_current_weather":
        result = simulate_weather_api(
            location=arguments["location"], unit=arguments.get("unit", "celsius")
        )
        return json.dumps(result)
    elif function_name == "calculate":
        result = simulate_calculator(arguments["expression"])
        return json.dumps(result)
    else:
        return json.dumps({"error": f"Unknown function: {function_name}"})


def main() -> None:
    """Main example demonstrating tool use."""

    # Available tools
    tools = [weather_tool, calculator_tool]

    # Test cases for different scenarios
    test_cases = [
        "What's the weather like in San Francisco?",
        "Calculate 15 * 8 + 32",
        "What's the weather in London in Fahrenheit and also calculate 100 / 4?",
        "Hello! How are you doing today?",  # No tool use expected
    ]

    for i, user_message in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {user_message}")
        print("=" * 60)

        # Start conversation
        messages = [
            Message(
                role="system",
                content="You are a helpful assistant with access to weather information and a calculator. Use the tools when appropriate to help answer user questions.",
            ),
            Message(role="user", content=user_message),
        ]

        # Make initial request with tools
        response = client.create_chat_completion(model=LLM_NAME, messages=messages, tools=tools)

        assistant_message = response.choices[0].message
        print(f"Assistant: {assistant_message.content or '(Making tool calls...)'}")

        # Check if the model made tool calls
        if assistant_message.tool_calls:
            print(f"\nTool calls made: {len(assistant_message.tool_calls)}")

            # Add assistant message to conversation
            messages.append(
                Message(
                    role="assistant",
                    content=assistant_message.content,
                    tool_calls=[
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                )
            )

            # Execute each tool call and add results
            for tool_call in assistant_message.tool_calls:
                print(f"\nExecuting: {tool_call.function.name}")
                print(f"Arguments: {tool_call.function.arguments}")

                # Execute the tool call
                tool_result = execute_tool_call(tool_call)
                print(f"Result: {tool_result}")

                # Add tool result to conversation
                messages.append(
                    Message(role="tool", tool_call_id=tool_call.id, content=tool_result)
                )

            # Get final response after tool execution
            final_response = client.create_chat_completion(
                model=LLM_NAME, messages=messages, tools=tools
            )

            print(f"\nFinal Assistant Response: {final_response.choices[0].message.content}")
        else:
            print("No tool calls were made.")


if __name__ == "__main__":
    main()
