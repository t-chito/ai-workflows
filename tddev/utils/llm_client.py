"""LLM Client for TDDev framework - Claude Agent SDK compatible.

Simplified LLM client that works seamlessly with Claude Agent SDK environment.
Supports both Anthropic (Claude) and OpenAI (GPT) models.

Based on arXiv:2509.25297v2 implementation.
"""

import os
from typing import List, Dict, Optional, Union
from loguru import logger


class LLMClient:
    """Unified LLM client supporting multiple providers.

    Designed to work with Claude Agent SDK environment while maintaining
    compatibility with standard Anthropic and OpenAI APIs.
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0,
        max_tokens: int = 8192,
    ):
        """Initialize LLM client.

        Args:
            provider: "anthropic", "openai", or "claude-agent-sdk"
            model: Model identifier
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None

        # Initialize based on provider
        if self.provider in ["anthropic", "claude-agent-sdk"]:
            self._init_anthropic()
        elif self.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Use 'anthropic', 'openai', or 'claude-agent-sdk'"
            )

        logger.info(f"✓ Initialized LLMClient: {provider}/{model}")

    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed.\n"
                "Install it with: pip install anthropic"
            )

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set.\n"
                "Set it with: export ANTHROPIC_API_KEY='your-key'\n"
                "Or add it to your environment"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        logger.debug(f"Anthropic client initialized with model: {self.model}")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package not installed.\n"
                "Install it with: pip install openai"
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not set.\n"
                "Set it with: export OPENAI_API_KEY='your-key'"
            )

        self.client = openai.OpenAI(api_key=api_key)
        logger.debug(f"OpenAI client initialized with model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Send chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System message (optional)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response

        Example:
            >>> client = LLMClient()
            >>> response = client.chat([
            ...     {"role": "user", "content": "Hello!"}
            ... ])
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        if self.provider in ["anthropic", "claude-agent-sdk"]:
            return self._chat_anthropic(messages, system, temp, max_tok, **kwargs)
        elif self.provider == "openai":
            return self._chat_openai(messages, system, temp, max_tok, **kwargs)

    def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Anthropic-specific chat completion."""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        if system:
            params["system"] = system

        try:
            response = self.client.messages.create(**params)
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise RuntimeError(f"Failed to get response from Anthropic: {e}")

    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """OpenAI-specific chat completion."""
        # Add system message to messages list for OpenAI
        if system:
            messages = [{"role": "system", "content": system}] + messages

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to get response from OpenAI: {e}")

    def chat_with_vision(
        self,
        text: str,
        images: Union[str, List[str]],
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chat with vision (multimodal support).

        Args:
            text: Text prompt
            images: Image path(s) or URL(s)
            system: System message
            **kwargs: Additional arguments

        Returns:
            Generated text response

        Example:
            >>> client = LLMClient()
            >>> response = client.chat_with_vision(
            ...     "What's in this image?",
            ...     "design.png"
            ... )
        """
        if isinstance(images, str):
            images = [images]

        if self.provider in ["anthropic", "claude-agent-sdk"]:
            return self._chat_vision_anthropic(text, images, system, **kwargs)
        elif self.provider == "openai":
            return self._chat_vision_openai(text, images, system, **kwargs)

    def _chat_vision_anthropic(
        self,
        text: str,
        images: List[str],
        system: Optional[str],
        **kwargs
    ) -> str:
        """Anthropic vision chat."""
        import base64
        from pathlib import Path

        content = []

        # Add images
        for img_path in images:
            if Path(img_path).exists():
                with open(img_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")

                # Detect image type
                suffix = Path(img_path).suffix.lower()
                media_type = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".webp": "image/webp",
                    ".gif": "image/gif"
                }.get(suffix, "image/jpeg")

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data
                    }
                })
            else:
                logger.warning(f"Image not found: {img_path}")

        # Add text
        content.append({"type": "text", "text": text})

        messages = [{"role": "user", "content": content}]
        return self._chat_anthropic(
            messages, system, self.temperature, self.max_tokens, **kwargs
        )

    def _chat_vision_openai(
        self,
        text: str,
        images: List[str],
        system: Optional[str],
        **kwargs
    ) -> str:
        """OpenAI vision chat."""
        from pathlib import Path

        content = [{"type": "text", "text": text}]

        # Add images
        for img_path in images:
            if Path(img_path).exists():
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"file://{img_path}"}
                })
            else:
                # Assume URL
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img_path}
                })

        messages = [{"role": "user", "content": content}]
        return self._chat_openai(
            messages, system, self.temperature, self.max_tokens, **kwargs
        )


# Convenience functions for Claude Agent SDK style usage
def create_client(
    provider: str = "anthropic",
    model: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """Create an LLM client with sensible defaults (Claude Agent SDK style).

    Args:
        provider: "anthropic", "openai", or "claude-agent-sdk"
        model: Model name (uses default if not provided)
        **kwargs: Additional arguments for LLMClient

    Returns:
        LLMClient instance

    Example:
        >>> client = create_client("anthropic")
        >>> response = client.chat([{"role": "user", "content": "Hi"}])
    """
    if model is None:
        if provider in ["anthropic", "claude-agent-sdk"]:
            model = "claude-sonnet-4-5-20250929"
        elif provider == "openai":
            model = "gpt-4.1"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    return LLMClient(provider=provider, model=model, **kwargs)


def quick_chat(prompt: str, provider: str = "anthropic", **kwargs) -> str:
    """Quick chat for simple one-off queries (Claude Agent SDK style).

    Args:
        prompt: User prompt
        provider: LLM provider
        **kwargs: Additional arguments

    Returns:
        Response text

    Example:
        >>> response = quick_chat("What is 2+2?")
        >>> print(response)
    """
    client = create_client(provider, **kwargs)
    return client.chat([{"role": "user", "content": prompt}])


# Example usage
if __name__ == "__main__":
    import sys

    print("TDDev LLM Client - Claude Agent SDK Compatible\n")

    # Example 1: Standard usage
    print("Example 1: Standard usage")
    try:
        client = create_client("anthropic")
        response = client.chat([
            {"role": "user", "content": "Say hello in exactly 5 words."}
        ])
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")
        print("Make sure ANTHROPIC_API_KEY is set!\n")

    # Example 2: Quick chat
    print("Example 2: Quick chat")
    try:
        response = quick_chat("What is the capital of France?")
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    print("For more examples, see the TDDev documentation.")
