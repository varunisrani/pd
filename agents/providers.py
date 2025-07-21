"""Model provider abstraction following main_agent_reference patterns."""

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from .settings import settings


def get_llm_model():
    """Get configured LLM model based on environment settings."""
    
    if settings.llm_provider.lower() == "openai":
        provider = OpenAIProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key
        )
        return OpenAIModel(settings.llm_model, provider=provider)
    
    elif settings.llm_provider.lower() == "anthropic":
        provider = AnthropicProvider(api_key=settings.llm_api_key)
        return AnthropicModel(settings.llm_model, provider=provider)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")