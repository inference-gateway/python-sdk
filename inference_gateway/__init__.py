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
    CompletionUsage,
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    Function,
    ListModelsResponse,
    Message,
    MessageRole,
    Model,
    Provider,
    SSEvent,
)

__version__ = "0.4.0"
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
    "MessageRole",
    "ListModelsResponse",
    "CreateChatCompletionRequest",
    "CreateChatCompletionResponse",
    "SSEvent",
    "Model",
    "CompletionUsage",
    "ChatCompletionMessageToolCall",
    "Function",
]
