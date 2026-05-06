"""Inference Gateway Python SDK.

A modern Python SDK for the Inference Gateway API with full OpenAPI support
and type safety using Pydantic v2.
"""

from inference_gateway.client import (
    InferenceGatewayAPIError,
    InferenceGatewayClient,
    InferenceGatewayError,
    InferenceGatewayValidationError,
)
from inference_gateway.models import (
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallChunk,
    CompletionUsage,
    ContentPart,
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    FinishReason,
    FunctionObject,
    Google,
    ImageContentPart,
    ImageURL,
    ListModelsResponse,
    Message,
    MessageContent,
    MessageRole,
    Model,
    Provider,
    SSEvent,
    TextContentPart,
    ToolCallExtraContent,
)

__version__ = "0.5.0"
__all__ = [
    # Client classes
    "InferenceGatewayClient",
    # Exceptions
    "InferenceGatewayError",
    "InferenceGatewayAPIError",
    "InferenceGatewayValidationError",
    # Core models
    "Provider",
    "Message",
    "MessageContent",
    "MessageRole",
    "ListModelsResponse",
    "CreateChatCompletionRequest",
    "CreateChatCompletionResponse",
    "CreateChatCompletionStreamResponse",
    "SSEvent",
    "Model",
    "CompletionUsage",
    "ChatCompletionMessageToolCall",
    "ChatCompletionMessageToolCallChunk",
    "FunctionObject",
    "FinishReason",
    "ToolCallExtraContent",
    "Google",
    # Multimodal content
    "ContentPart",
    "TextContentPart",
    "ImageContentPart",
    "ImageURL",
]
