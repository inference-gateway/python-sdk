from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import requests


class Provider(str, Enum):
    """Supported LLM providers"""

    OLLAMA = "ollama"
    GROQ = "groq"
    OPENAI = "openai"
    GOOGLE = "google"
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


class Model:
    """Represents an LLM model"""

    def __init__(self, id: str, object: str, owned_by: str, created: int):
        self.id = id
        self.object = object
        self.owned_by = owned_by
        self.created = created


class ProviderModels:
    """Groups models by provider"""

    def __init__(self, provider: Provider, models: List[Model]):
        self.provider = provider
        self.models = models


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
        payload = {"model": model, "messages": [msg.to_dict() for msg in messages]}

        response = self.session.post(
            f"{self.base_url}/llms/{provider.value}/generate", json=payload
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        return response.status_code == 200
