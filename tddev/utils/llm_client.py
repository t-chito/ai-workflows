"""LLM Client for TDDev framework.

Supports both Anthropic (Claude) and OpenAI (GPT) models.
Based on arXiv:2509.25297v2 implementation.
"""

import os
from typing import List, Dict, Optional, Any, Union
from loguru import logger


class LLMClient:
    """Unified LLM client supporting multiple providers."""

    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0,
        max_tokens: int = 8192,
    ):
        """Initialize LLM client.

        Args:
            provider: "anthropic" or "openai"
            model: Model identifier
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize provider-specific client
        if self.provider == "anthropic":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY environment variable not set")
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info(f"Initialized Anthropic client with model: {model}")
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        elif self.provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                self.client = openai.OpenAI(api_key=api_key)
                logger.info(f"Initialized OpenAI client with model: {model}")
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

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
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        if self.provider == "anthropic":
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
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }

            if system:
                params["system"] = system

            response = self.client.messages.create(**params)
            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """OpenAI-specific chat completion."""
        try:
            # Add system message to messages list for OpenAI
            if system:
                messages = [{"role": "system", "content": system}] + messages

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
            raise

    def chat_with_vision(
        self,
        text: str,
        images: Union[str, List[str]],
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chat with vision (multimodal).

        Args:
            text: Text prompt
            images: Image path(s) or URL(s)
            system: System message
            **kwargs: Additional arguments

        Returns:
            Generated text response
        """
        if isinstance(images, str):
            images = [images]

        if self.provider == "anthropic":
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

        # Add text
        content.append({"type": "text", "text": text})

        messages = [{"role": "user", "content": content}]
        return self._chat_anthropic(messages, system, self.temperature, self.max_tokens, **kwargs)

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
                # OpenAI supports local file paths
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
        return self._chat_openai(messages, system, self.temperature, self.max_tokens, **kwargs)


# Example usage
if __name__ == "__main__":
    # Test Anthropic client
    client = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    response = client.chat([
        {"role": "user", "content": "Hello, how are you?"}
    ])
    print(response)
