# Tools Example

This example demonstrates how to use function calling (tools) with the Inference Gateway Python SDK.

## Overview

The example shows:

- How to define tools using the standard OpenAI function calling format
- Making chat completions with tools enabled
- Handling tool calls from the model
- Simulating tool execution
- Continuing conversations with tool results

## Tools Defined

1. **Weather Tool** - Get current weather for a location
2. **Calculator Tool** - Perform basic mathematical calculations

## Running the Example

```bash
# Set the model (optional, defaults to openai/gpt-4)
export LLM_NAME="openai/gpt-4"

# Run the example
python examples/tools/main.py
```

## Tool Format

Tools are defined using type-safe Pydantic models from the SDK:

```python
from inference_gateway.models import ChatCompletionTool, FunctionObject, FunctionParameters

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
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use"
                }
            },
            required=["location"]
        )
    )
)
```

This approach provides:

- **Type Safety**: Full type checking at development time
- **IDE Support**: Better autocomplete and error detection
- **Validation**: Automatic validation of tool definitions
- **Documentation**: Self-documenting code with proper types

## Test Cases

The example runs through several test cases:

1. Weather query: "What's the weather like in San Francisco?"
2. Math calculation: "Calculate 15 \* 8 + 32"
3. Multiple tools: "What's the weather in London in Fahrenheit and also calculate 100 / 4?"
4. No tools needed: "Hello! How are you doing today?"

## Key Concepts

- **Type-Safe Tool Definition**: Use Pydantic models for tool definitions to ensure type safety
- **Function Parameters**: Define proper JSON schema for function parameters with validation
- **Tool Calls**: Handle when the model decides to call a function
- **Tool Results**: Provide function results back to continue the conversation
- **Multiple Tools**: Models can call multiple tools in a single response
- **Conversation Flow**: Maintain proper message history with tool calls and results
- **Type Safety**: Full type checking for tool calls and responses

## Notes

- This example simulates tool execution - in production you'd integrate with real APIs
- The calculator uses `eval()` for simplicity - use a proper math parser in production
- Tool calls are optional - the model will only use them when appropriate
