"""Inference Gateway Python SDK.

A modern Python SDK for the Inference Gateway API with full OpenAPI support
and type safety using Pydantic v2.
"""

from importlib.metadata import PackageNotFoundError, version

from inference_gateway.client import (
    InferenceGatewayAPIError,
    InferenceGatewayClient,
    InferenceGatewayError,
    InferenceGatewayValidationError,
)
from inference_gateway.models import (
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallChunk,
    ChatCompletionNamedToolChoice,
    ChatCompletionToolChoiceOption,
    CompletionUsage,
    ContentPart,
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    CreateResponseRequest,
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
    Response,
    ResponseError,
    ResponseFormatJsonObject,
    ResponseFormatJsonSchema,
    ResponseFormatText,
    ResponseFunctionToolCall,
    ResponseInput,
    ResponseInputImage,
    ResponseInputItem,
    ResponseInputText,
    ResponseOutputItem,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoning,
    ResponseReasoningItem,
    ResponseRole,
    ResponseStatus,
    ResponseStreamEvent,
    ResponseTextConfig,
    ResponseTool,
    ResponseToolChoice,
    ResponseUsage,
    SSEvent,
    TextContentPart,
    ToolCallExtraContent,
)

try:
    __version__ = version("inference-gateway")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

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
    # Tool choice
    "ChatCompletionToolChoiceOption",
    "ChatCompletionNamedToolChoice",
    # Structured outputs / response format
    "ResponseFormatText",
    "ResponseFormatJsonObject",
    "ResponseFormatJsonSchema",
    # Multimodal content
    "ContentPart",
    "TextContentPart",
    "ImageContentPart",
    "ImageURL",
    # Responses API
    "CreateResponseRequest",
    "Response",
    "ResponseStreamEvent",
    "ResponseInput",
    "ResponseInputItem",
    "ResponseInputText",
    "ResponseInputImage",
    "ResponseTool",
    "ResponseToolChoice",
    "ResponseReasoning",
    "ResponseTextConfig",
    "ResponseStatus",
    "ResponseError",
    "ResponseOutputItem",
    "ResponseOutputMessage",
    "ResponseOutputText",
    "ResponseFunctionToolCall",
    "ResponseReasoningItem",
    "ResponseUsage",
    "ResponseRole",
]
