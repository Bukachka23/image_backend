from datetime import datetime
from enum import Enum

from src.domain.value_objects.credits import Credits
from src.domain.value_objects.money import Money


class TransactionType(Enum):
    """Types of credit transactions"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"


class CreditTransaction:
    """Entity representing a credit transaction"""

    def __init__(
            self,
            id: int | None,
            user_id: int,
            transaction_type: TransactionType,
            credits: Credits,
            amount: Money | None = None,
            payment_id: str | None = None,
            description: str | None = None,
            created_at: datetime | None = None
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._type = transaction_type
        self._credits = credits
        self._amount = amount
        self._payment_id = payment_id
        self._description = description
        self._created_at = created_at or datetime.now()

        self._validate()

    def _validate(self) -> None:
        """Validate transaction invariants"""
        if self._type == TransactionType.PURCHASE and not self._payment_id:
            raise ValueError("Purchase transactions must have a payment ID")

        if self._type == TransactionType.PURCHASE and not self._amount:
            raise ValueError("Purchase transactions must have an amount")

        if self._type == TransactionType.USAGE and self._credits.value > 0:
            raise ValueError("Usage transactions must have negative credits")

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def transaction_type(self) -> TransactionType:
        return self._type

    @property
    def credits(self) -> Credits:
        return self._credits

    @property
    def amount(self) -> Money | None:
        return self._amount

    @property
    def payment_id(self) -> str | None:
        return self._payment_id

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @staticmethod
    def create_purchase(
            user_id: int,
            credits: Credits,
            amount: Money,
            payment_id: str,
            description: str
    ) -> "CreditTransaction":
        """Factory method for purchase transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.PURCHASE,
            credits=credits,
            amount=amount,
            payment_id=payment_id,
            description=description
        )

    @staticmethod
    def create_usage(
            user_id: int,
            credits: Credits,
            description: str
    ) -> "CreditTransaction":
        """Factory method for usage transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.USAGE,
            credits=Credits(-abs(credits.value)),
            description=description
        )

    @staticmethod
    def create_refund(
            user_id: int,
            credits: Credits,
            description: str
    ) -> "CreditTransaction":
        """Factory method for refund transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.REFUND,
            credits=credits,
            description=description
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, CreditTransaction):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
