"""Unit tests for LLMClient (with mocking)."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tddev.utils.llm_client import LLMClient


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    with patch('anthropic.Anthropic') as mock:
        yield mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('openai.OpenAI') as mock:
        yield mock


def test_llm_client_initialization_anthropic(mock_anthropic_client, monkeypatch):
    """Test LLMClient initialization with Anthropic."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    client = LLMClient(
        provider="anthropic",
        model="claude-sonnet-4-5-20250929"
    )

    assert client.provider == "anthropic"
    assert client.model == "claude-sonnet-4-5-20250929"
    assert client.temperature == 0
    assert client.max_tokens == 8192


def test_llm_client_initialization_openai(mock_openai_client, monkeypatch):
    """Test LLMClient initialization with OpenAI."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = LLMClient(
        provider="openai",
        model="gpt-4.1"
    )

    assert client.provider == "openai"
    assert client.model == "gpt-4.1"


def test_llm_client_missing_api_key():
    """Test that missing API key raises error."""
    with pytest.raises(ValueError, match="API_KEY"):
        LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")


def test_llm_client_chat_anthropic(mock_anthropic_client, monkeypatch):
    """Test chat with Anthropic."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    # Setup mock response
    mock_response = Mock()
    mock_response.content = [Mock(text="Hello from Claude!")]
    mock_client_instance = Mock()
    mock_client_instance.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client_instance

    client = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    response = client.chat([{"role": "user", "content": "Hello"}])

    assert response == "Hello from Claude!"
    mock_client_instance.messages.create.assert_called_once()


def test_llm_client_unsupported_provider():
    """Test unsupported provider raises error."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        LLMClient(provider="invalid", model="model")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
