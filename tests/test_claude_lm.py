"""
Unit tests for Claude LanguageModel wrapper.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from dspy_prompt_fixer.claude_lm import ClaudeLM


class TestClaudeLM:
    """Test cases for ClaudeLM class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api_key = "test-api-key-123"
        self.mock_model = "claude-3-opus-20240229"

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            lm = ClaudeLM(api_key=self.mock_api_key, model=self.mock_model)

            assert lm.api_key == self.mock_api_key
            assert lm.model == self.mock_model
            assert lm.client is not None
            mock_anthropic.assert_called_once_with(api_key=self.mock_api_key)

    def test_init_with_env_var(self):
        """Test initialization with API key from environment variable."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': self.mock_api_key}):
            with patch('anthropic.Anthropic') as mock_anthropic:
                lm = ClaudeLM(model=self.mock_model)

                assert lm.api_key == self.mock_api_key
                assert lm.model == self.mock_model
                mock_anthropic.assert_called_once_with(api_key=self.mock_api_key)

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY must be provided"):
                ClaudeLM()

    def test_init_with_env_config(self):
        """Test initialization with environment configuration."""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': self.mock_api_key,
            'DSPY_TEMPERATURE': '0.5',
            'DSPY_MAX_TOKENS': '512'
        }):
            with patch('anthropic.Anthropic'):
                lm = ClaudeLM()

                assert lm.temperature == 0.5
                assert lm.max_tokens == 512

    def test_call_success(self):
        """Test successful API call."""
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Test response"
        mock_response.content = [mock_content]

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            lm = ClaudeLM(api_key=self.mock_api_key)
            result = lm("Test prompt")

            assert result == "Test response"
            mock_client.messages.create.assert_called_once()

    def test_call_with_custom_params(self):
        """Test API call with custom parameters."""
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Test response"
        mock_response.content = [mock_content]

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            lm = ClaudeLM(api_key=self.mock_api_key)
            result = lm("Test prompt", temperature=0.3, max_tokens=256)

            call_args = mock_client.messages.create.call_args
            assert call_args[1]['temperature'] == 0.3
            assert call_args[1]['max_tokens'] == 256

    def test_call_empty_response(self):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.content = []

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            lm = ClaudeLM(api_key=self.mock_api_key)
            result = lm("Test prompt")

            assert result == ""

    def test_call_api_error(self):
        """Test handling of API errors."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API Error")
            mock_anthropic.return_value = mock_client

            lm = ClaudeLM(api_key=self.mock_api_key)

            with pytest.raises(RuntimeError, match="Error calling Claude API"):
                lm("Test prompt")

    def test_get_config(self):
        """Test getting configuration."""
        with patch('anthropic.Anthropic'):
            lm = ClaudeLM(api_key=self.mock_api_key, model=self.mock_model)
            config = lm.get_config()

            assert config['model'] == self.mock_model
            assert config['provider'] == 'anthropic'
            assert 'temperature' in config
            assert 'max_tokens' in config
