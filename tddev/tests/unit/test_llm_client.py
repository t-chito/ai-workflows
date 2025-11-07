"""Unit tests for LLMClient (with mocking)."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tddev.utils.llm_client import LLMClient, create_client, quick_chat


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


def test_create_client_defaults(mock_anthropic_client, monkeypatch):
    """Test create_client convenience function with defaults."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    client = create_client()

    assert client.provider == "anthropic"
    assert client.model == "claude-sonnet-4-5-20250929"
    assert isinstance(client, LLMClient)


def test_create_client_custom_params(mock_anthropic_client, monkeypatch):
    """Test create_client with custom parameters."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    client = create_client(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=4096
    )

    assert client.model == "claude-3-5-sonnet-20241022"
    assert client.temperature == 0.7
    assert client.max_tokens == 4096


def test_quick_chat(mock_anthropic_client, monkeypatch):
    """Test quick_chat convenience function."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    # Setup mock response
    mock_response = Mock()
    mock_response.content = [Mock(text="The answer is 4")]
    mock_client_instance = Mock()
    mock_client_instance.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client_instance

    response = quick_chat("What is 2+2?")

    assert response == "The answer is 4"
    mock_client_instance.messages.create.assert_called_once()


def test_claude_agent_sdk_provider(mock_anthropic_client, monkeypatch):
    """Test using claude-agent-sdk as provider."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    client = LLMClient(
        provider="claude-agent-sdk",
        model="claude-sonnet-4-5-20250929"
    )

    # Should be treated as anthropic internally
    assert client.provider == "claude-agent-sdk"
    assert client.model == "claude-sonnet-4-5-20250929"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
