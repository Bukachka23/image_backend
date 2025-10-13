import re
from typing import Any


class Email:
    """Email value object with validation"""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, value: str):
        self._value = self._validate_and_normalize(value)

    def _validate_and_normalize(self, value: str) -> str:
        if not value:
            raise ValueError("Email cannot be empty")

        normalized = value.strip().lower()

        if not self.EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email format: {value}")

        if len(normalized) > 254:  # RFC 5321
            raise ValueError("Email exceeds maximum length")

        return normalized

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email('{self._value}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Email):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
