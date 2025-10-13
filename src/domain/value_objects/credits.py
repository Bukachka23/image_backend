from typing import Any


class Credits:
    """Credits value object representing user credits"""

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Credits must be an integer")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __add__(self, other: "Credits") -> "Credits":
        if not isinstance(other, Credits):
            raise TypeError("Can only add Credits to Credits")
        return Credits(self._value + other._value)

    def __sub__(self, other: "Credits") -> "Credits":
        if not isinstance(other, Credits):
            raise TypeError("Can only subtract Credits from Credits")
        return Credits(self._value - other._value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Credits):
            return False
        return self._value == other._value

    def __lt__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value < other._value

    def __le__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value <= other._value

    def __gt__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value > other._value

    def __ge__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value >= other._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Credits({self._value})"

    def __hash__(self) -> int:
        return hash(self._value)
