from research_agent.config import settings
from research_agent.llm.base import LLMProvider
from research_agent.llm.ollama_provider import OllamaProvider
from research_agent.llm.gemini_provider import GeminiProvider
from research_agent.llm.mock_provider import MockProvider

def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower().strip()
    if provider == "mock":
        return MockProvider(model_name=settings.default_model)
    elif provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model_name=settings.default_model
        )
    elif provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in configuration")
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.default_model
        )
    elif provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set in configuration")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model_name=settings.default_model
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

__all__ = [
    "LLMProvider",
    "MockProvider",
    "OllamaProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "get_llm_provider"
]
