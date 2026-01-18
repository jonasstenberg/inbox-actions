"""Mock provider for testing without API calls."""

import hashlib

from providers.base import ClassificationResult, Provider


class MockProvider(Provider):
    """Mock provider that returns deterministic fake responses.

    Generates consistent results based on email content hash,
    so the same email always produces the same classification.
    """

    def __init__(self, api_key: str = "mock", model: str | None = None):
        # Accept any api_key (including empty) for testing convenience
        super().__init__(api_key or "mock", model)

    @property
    def default_model(self) -> str:
        return "mock-v1"

    @property
    def name(self) -> str:
        return "Mock"

    def _call_api(self, prompt: str) -> str:
        """Not used - MockProvider overrides classify() directly."""
        raise NotImplementedError("MockProvider does not make API calls")

    def classify(self, prompt: str) -> ClassificationResult:
        """Return deterministic classification based on prompt content."""
        # Generate consistent hash from prompt
        prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)

        # Deterministic but varied results based on hash
        needs_action = prompt_hash % 3 != 0  # ~67% need action
        priority_idx = prompt_hash % 3
        priorities = ["low", "medium", "high"]

        reasons = [
            "Contains deadline or due date",
            "Sender is marked as important",
            "Request requires response",
            "Informational only",
            "Automated notification",
        ]

        return ClassificationResult(
            needs_action=needs_action,
            priority=priorities[priority_idx],
            reason=reasons[prompt_hash % len(reasons)],
        )
