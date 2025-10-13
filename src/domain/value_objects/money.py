from decimal import ROUND_HALF_UP, Decimal
from typing import Any


class Money:
    """Money value object for handling currency"""

    def __init__(self, value: float, currency: str = "USD"):
        if value < 0:
            raise ValueError("Money cannot be negative")

        self._value = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self._currency = currency.upper()

    @property
    def value(self) -> float:
        return float(self._value)

    @property
    def currency(self) -> str:
        return self._currency

    def to_cents(self) -> int:
        """Convert to cents for payment processing"""
        return int(self._value * 100)

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self._currency != other._currency:
            raise ValueError("Cannot add different currencies")
        return Money(float(self._value + other._value), self._currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self._currency != other._currency:
            raise ValueError("Cannot subtract different currencies")
        result = float(self._value - other._value)
        if result < 0:
            raise ValueError("Money cannot be negative")
        return Money(result, self._currency)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self._value == other._value and self._currency == other._currency

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self._currency != other._currency:
            raise ValueError("Cannot compare different currencies")
        return self._value < other._value

    def __str__(self) -> str:
        return f"{self._currency} {self._value}"

    def __repr__(self) -> str:
        return f"Money({float(self._value)}, '{self._currency}')"

    def __hash__(self) -> int:
        return hash((self._value, self._currency))
