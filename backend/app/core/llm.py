"""LLM Provider abstraction using LangChain and Groq API.

Configured for high-throughput hypothesis generation and reflection using
fast open-weight models (e.g. openai/gpt-oss-120b, llama-3.3-70b-versatile).
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


def get_llm_client(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> BaseChatModel:
    """Instantiates a LangChain Chat model client based on environment variables.
    
    Defaults to Groq with openai/gpt-oss-120b or llama-3.3-70b-versatile.
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    target_model = model_name or os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-120b")

    if provider == "groq" or groq_api_key:
        from langchain_groq import ChatGroq
        
        # In case the user passed openai/gpt-oss-120b or a standard groq model
        return ChatGroq(
            model=target_model,
            groq_api_key=groq_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # Optional fallback providers
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=target_model if "/" not in target_model else "gpt-4o-mini",
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"Unsupported LLM provider '{provider}' or missing GROQ_API_KEY."
    )
