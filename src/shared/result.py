from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T]):
    """Base result class"""

    def is_success(self) -> bool:
        return isinstance(self, Success)

    def is_failure(self) -> bool:
        return isinstance(self, Failure)

    @property
    def value(self) -> T:
        if isinstance(self, Success):
            return self._value
        raise ValueError("Cannot get value from Failure")

    @property
    def error(self) -> Exception:
        if isinstance(self, Failure):
            return self._error
        raise ValueError("Cannot get error from Success")


class Success(Result[T]):
    """Represents a successful result"""

    def __init__(self, value: T):
        self._value = value

    def __repr__(self) -> str:
        return f"Success({self._value})"


class Failure(Result[T]):
    """Represents a failed result"""

    def __init__(self, error: Exception):
        self._error = error

    def __repr__(self) -> str:
        return f"Failure({self._error})"
