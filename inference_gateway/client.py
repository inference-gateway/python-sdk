from typing import Generator, Optional
import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
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


@dataclass
class GenerateResponse:
    """Response structure for token generation"""
    provider: str
    response: ResponseTokens

    @classmethod
    def from_dict(cls, data: dict) -> 'GenerateResponse':
        """Create GenerateResponse from dictionary data"""
        return cls(
            provider=data.get('provider', ''),
            response=ResponseTokens(**data.get('response', {}))
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

    def generate_content(self, provider: Provider, model: str, messages: List[Message]) -> Dict:
        payload = {"model": model, "messages": [
            msg.to_dict() for msg in messages]}

        response = self.session.post(
            f"{self.base_url}/llms/{provider.value}/generate", json=payload
        )
        response.raise_for_status()
        return response.json()

    def generate_content_stream(
        self,
        provider: Provider,
        model: str,
        messages: List[Message],
        use_sse: bool = False
    ) -> Generator[Union[GenerateResponse, dict], None, None]:
        """Stream content generation from the model

        Args:
            provider: The provider to use
            model: Name of the model to use
            messages: List of messages for the conversation
            use_sse: Whether to use Server-Sent Events format

        Yields:
            Either GenerateResponse objects (for raw JSON) or dicts (for SSE)
        """
        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "stream": True,
            "ssevents": use_sse
        }

        with self.session.post(
            f"{self.base_url}/llms/{provider.value}/generate",
            json=payload,
            stream=True
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    if use_sse and line.startswith(b'data: '):
                        # Handle SSE format
                        data = json.loads(line.decode(
                            'utf-8').replace('data: ', ''))
                        yield data
                    else:
                        # Handle raw JSON format
                        data = json.loads(line)
                        yield GenerateResponse.from_dict(data)

    def health_check(self) -> bool:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        return response.status_code == 200
