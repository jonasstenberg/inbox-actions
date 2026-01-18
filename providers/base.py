"""Base provider interface for AI classification."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Result of email classification."""

    needs_action: bool
    priority: str
    reason: str


class Provider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize provider.

        Args:
            api_key: API key for the provider.
            model: Optional model override. If not specified, uses provider default.
        """
        self.api_key = api_key
        self.model = model or self.default_model

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model to use for this provider."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this provider."""
        raise NotImplementedError

    @abstractmethod
    def classify(self, prompt: str) -> ClassificationResult:
        """Classify an email using the provider's API.

        Args:
            prompt: The formatted prompt containing email data.

        Returns:
            ClassificationResult with needs_action, priority, and reason.
        """
        raise NotImplementedError

    def parse_response(self, content: str) -> ClassificationResult:
        """Parse JSON response from AI model.

        Handles markdown code blocks and extracts JSON.

        Args:
            content: Raw response content from the model.

        Returns:
            ClassificationResult parsed from the response.
        """
        content = content.strip()

        # Extract JSON from markdown code blocks
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        try:
            data = json.loads(content)
            return ClassificationResult(
                needs_action=data.get("needs_action", False),
                priority=data.get("priority", "low"),
                reason=data.get("reason", ""),
            )
        except json.JSONDecodeError:
            return ClassificationResult(
                needs_action=False,
                priority="low",
                reason="Failed to parse response",
            )
