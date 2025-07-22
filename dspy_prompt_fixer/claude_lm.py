"""
Claude LanguageModel wrapper for DSPy integration.
"""

import os
from typing import Optional, Dict, Any, List
import anthropic
from dspy.clients import LM


class ClaudeLM(LM):
    """Custom LanguageModel wrapper for Anthropic's Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
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
        self.max_tokens = int(os.getenv("DSPY_MAX_TOKENS", "4096"))

        # Add required attributes for DSPy compatibility
        self.kwargs = {}
        self.provider = "anthropic"

    def __call__(self, prompt: str = None, messages: List[Dict[str, str]] = None, **kwargs) -> str:
        """
        Call Claude API with the given prompt or messages.

        Args:
            prompt: The prompt to send to Claude (for backward compatibility).
            messages: List of message dictionaries (for DSPy compatibility).
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Claude's response as a string.
        """
        try:
            # Use kwargs or fall back to instance defaults
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)

            # Handle DSPy's calling pattern
            if messages is not None:
                # Extract system message if present
                system_message = None
                user_messages = []

                for message in messages:
                    if message.get("role") == "system":
                        system_message = message.get("content")
                    else:
                        user_messages.append(message)

                # Prepare API call parameters
                api_params = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": user_messages
                }

                # Add system message as top-level parameter if present
                if system_message:
                    api_params["system"] = system_message

                response = self.client.messages.create(**api_params)

            elif prompt is not None:
                # Backward compatibility with direct prompt
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            else:
                raise ValueError("Either 'prompt' or 'messages' must be provided")

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

    # Add required methods for DSPy compatibility
    def basic_request(self, prompt: str, **kwargs) -> str:
        """Basic request method for DSPy compatibility."""
        return self.__call__(prompt, **kwargs)

    def request(self, prompt: str, **kwargs) -> str:
        """Request method for DSPy compatibility."""
        return self.__call__(prompt, **kwargs)
