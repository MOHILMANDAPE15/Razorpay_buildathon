"""LLM Provider abstraction supporting Groq, Gemini, OpenAI, and Anthropic.

Provider selected via LLM_PROVIDER env var. Default: groq.
Supported: groq, gemini, openai, anthropic.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


def get_llm_client(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> BaseChatModel:
    """Instantiates a LangChain Chat model client based on environment variables.

    Provider priority: LLM_PROVIDER env var (groq | gemini | openai | anthropic).
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    target_model = model_name or os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-120b")

    if provider == "gemini" and gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=target_model,
            google_api_key=gemini_api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

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


def extract_response_text(response) -> str:
    """Normalizes LLM response content to a plain string.

    Handles:
    - Gemini 3.6 Flash: content is a list of dicts [{'type':'text','text':'...'}]
    - Qwen/Groq: content is a string, may contain <think>...</think> blocks
    - Standard string responses

    Returns:
        Plain text string with thinking blocks stripped.
    """
    content = response.content

    # Gemini thinking model: content is a list of parts
    if isinstance(content, list):
        text_parts = [
            p.get("text", "") for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        ]
        content = " ".join(text_parts).strip()

    # Ensure string
    content = str(content)

    # Strip Qwen/DeepSeek thinking blocks
    if "<think>" in content and "</think>" in content:
        content = content.split("</think>", 1)[1].strip()

    return content
