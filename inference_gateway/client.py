from typing import Generator, Optional, Union, List, Dict, Optional
import json
from dataclasses import dataclass
from enum import Enum
import requests


class Provider(str, Enum):
    """Supported LLM providers"""

    OLLAMA = "ollama"
    GROQ = "groq"
    OPENAI = "openai"
    CLOUDFLARE = "cloudflare"
    COHERE = "cohere"


class Role(str, Enum):
    """Message role types"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: Role
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format with string values"""
        return {"role": self.role.value, "content": self.content}


@dataclass
class Model:
    """Represents an LLM model"""

    name: str


@dataclass
class ProviderModels:
    """Groups models by provider"""

    provider: Provider
    models: List[Model]


@dataclass
class ResponseTokens:
    """Response tokens structure as defined in the API spec"""

    role: str
    model: str
    content: str

    @classmethod
    def from_dict(cls, data: dict) -> "ResponseTokens":
        """Create ResponseTokens from dictionary data

        Args:
            data: Dictionary containing response data

        Returns:
            ResponseTokens instance

        Raises:
            TypeError: If data is not a dictionary
            ValueError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data)}")

        required = ["role", "model", "content"]
        missing = [field for field in required if field not in data]

        if missing:
            raise ValueError(
                f"Missing required arguments: {
                    ', '.join(missing)}"
            )

        return cls(role=data["role"], model=data["model"], content=data["content"])


@dataclass
class GenerateResponse:
    """Response structure for token generation"""

    provider: str
    response: ResponseTokens

    @classmethod
    def from_dict(cls, data: dict) -> "GenerateResponse":
        """Create GenerateResponse from dictionary data"""
        return cls(
            provider=data.get("provider", ""), response=ResponseTokens(**data.get("response", {}))
        )


class InferenceGatewayClient:
    """Client for interacting with the Inference Gateway API"""

    def __init__(self, base_url: str, token: Optional[str] = None):
        """Initialize the client with base URL and optional auth token"""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def list_models(self) -> List[ProviderModels]:
        """List all available language models"""
        response = self.session.get(f"{self.base_url}/llms")
        response.raise_for_status()
        return response.json()

    def list_providers_models(self, provider: Provider) -> List[Model]:
        """List models for a specific provider"""
        response = self.session.get(f"{self.base_url}/llms/{provider.value}")
        response.raise_for_status()
        return response.json()

    def _parse_sse_chunk(self, chunk: bytes) -> dict:
        """Parse an SSE message chunk into structured event data

        Args:
            chunk: Raw SSE message chunk in bytes format

        Returns:
            dict: Parsed SSE message with event type and data fields

        Raises:
            json.JSONDecodeError: If chunk format or content is invalid
        """
        if not isinstance(chunk, bytes):
            raise TypeError(f"Expected bytes, got {type(chunk)}")

        try:
            decoded = chunk.decode("utf-8")
            message = {}

            for line in (l.strip() for l in decoded.split("\n") if l.strip()):
                if line.startswith("event: "):
                    message["event"] = line.removeprefix("event: ")
                elif line.startswith("data: "):
                    try:
                        json_str = line.removeprefix("data: ")
                        data = json.loads(json_str)
                        if not isinstance(data, dict):
                            raise json.JSONDecodeError(
                                f"Invalid SSE data format - expected object, got: {
                                    json_str}",
                                json_str,
                                0,
                            )
                        message["data"] = data
                    except json.JSONDecodeError as e:
                        raise json.JSONDecodeError(f"Invalid SSE JSON: {json_str}", e.doc, e.pos)

            if not message.get("data"):
                raise json.JSONDecodeError(
                    f"Missing or invalid data field in SSE message: {
                        decoded}",
                    decoded,
                    0,
                )

            return message

        except UnicodeDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid UTF-8 encoding in SSE chunk: {
                    chunk!r}",
                str(chunk),
                0,
            )

    def _parse_json_line(self, line: bytes) -> ResponseTokens:
        """Parse a single JSON line into GenerateResponse"""
        try:
            decoded_line = line.decode("utf-8")
            data = json.loads(decoded_line)
            return ResponseTokens.from_dict(data)
        except UnicodeDecodeError as e:
            raise json.JSONDecodeError(f"Invalid UTF-8 encoding: {line}", str(line), 0)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON response: {
                    decoded_line}",
                e.doc,
                e.pos,
            )

    def generate_content(self, provider: Provider, model: str, messages: List[Message]) -> Dict:
        payload = {"model": model, "messages": [msg.to_dict() for msg in messages]}

        response = self.session.post(
            f"{self.base_url}/llms/{provider.value}/generate", json=payload
        )
        response.raise_for_status()
        return response.json()

    def generate_content_stream(
        self, provider: Provider, model: str, messages: List[Message], use_sse: bool = False
    ) -> Generator[Union[ResponseTokens, dict], None, None]:
        """Stream content generation from the model

        Args:
            provider: The provider to use
            model: Name of the model to use
            messages: List of messages for the conversation
            use_sse: Whether to use Server-Sent Events format

        Yields:
            Either ResponseTokens objects (for raw JSON) or dicts (for SSE)
        """
        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "stream": True,
            "ssevents": use_sse,
        }

        response = self.session.post(
            f"{self.base_url}/llms/{provider.value}/generate", json=payload, stream=True
        )
        response.raise_for_status()

        if use_sse:
            buffer = []

            for line in response.iter_lines():
                if not line:
                    if buffer:
                        chunk = b"\n".join(buffer)
                        yield self._parse_sse_chunk(chunk)
                        buffer = []
                    continue

                buffer.append(line)
        else:
            for line in response.iter_lines():
                if not line:
                    continue
                yield self._parse_json_line(line)

    def health_check(self) -> bool:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        return response.status_code == 200
