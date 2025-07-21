"""Dependency injection for external services."""

from dataclasses import dataclass
from typing import Optional
import httpx
from .settings import settings


@dataclass
class ResearchAgentDependencies:
    """Dependencies for the research agent."""
    brave_api_key: str
    http_client: Optional[httpx.AsyncClient] = None
    
    def __post_init__(self):
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=settings.request_timeout,
                headers={"X-Subscription-Token": self.brave_api_key}
            )


@dataclass
class EmailAgentDependencies:
    """Dependencies for the email agent."""
    credentials_file: str
    token_file: str
    scopes: list[str]
    
    @classmethod
    def from_settings(cls) -> "EmailAgentDependencies":
        """Create dependencies from application settings."""
        return cls(
            credentials_file=settings.gmail_credentials_file,
            token_file=settings.gmail_token_file,
            scopes=settings.gmail_scopes
        )