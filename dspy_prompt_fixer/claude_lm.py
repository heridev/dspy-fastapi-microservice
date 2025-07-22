"""
Claude LanguageModel wrapper for DSPy integration.
"""

import os
from typing import Optional, Dict, Any
import anthropic
from dspy import LanguageModel


class ClaudeLM(LanguageModel):
    """Custom LanguageModel wrapper for Anthropic's Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize Claude LanguageModel.

        Args:
            api_key: Anthropic API key. If None, will try to get from environment.
            model: Claude model to use.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")

        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Default parameters
        self.temperature = float(os.getenv("DSPY_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("DSPY_MAX_TOKENS", "1024"))

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Call Claude API with the given prompt.

        Args:
            prompt: The prompt to send to Claude.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Claude's response as a string.
        """
        try:
            # Use kwargs or fall back to instance defaults
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                return ""

        except Exception as e:
            raise RuntimeError(f"Error calling Claude API: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """Get configuration for this language model."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "anthropic"
        }
