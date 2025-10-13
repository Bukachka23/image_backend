from datetime import datetime

from src.domain.entities.credit_transaction import CreditTransaction
from src.domain.exceptions import InsufficientCreditsError
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


class User:
    """User aggregate root - encapsulates all business logic related to users"""

    def __init__(
            self,
            id: int | None,
            email: Email,
            credits: Credits,
            stripe_customer_id: str | None = None,
            total_purchased: Money = None,
            created_at: datetime | None = None,
            updated_at: datetime | None = None
    ) -> None:
        self._id = id
        self._email = email
        self._credits = credits
        self._stripe_customer_id = stripe_customer_id
        self._total_purchased = total_purchased or Money(0.0)
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
        self._transactions: list[CreditTransaction] = []

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def credits(self) -> Credits:
        return self._credits

    @property
    def stripe_customer_id(self) -> str | None:
        return self._stripe_customer_id

    @property
    def total_purchased(self) -> Money:
        return self._total_purchased

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def pending_transactions(self) -> list[CreditTransaction]:
        return self._transactions.copy()

    def set_stripe_customer_id(self, customer_id: str) -> None:
        """Set the Stripe customer ID for payment processing"""
        if not customer_id:
            raise ValueError("Stripe customer ID cannot be empty")
        self._stripe_customer_id = customer_id
        self._mark_updated()

    def deduct_credits(self, amount: Credits, reason: str) -> CreditTransaction:
        """Deduct credits from user account."""
        if self._credits < amount:
            raise InsufficientCreditsError(
                f"Insufficient credits. Required: {amount.value}, Available: {self._credits.value}"
            )

        self._credits = self._credits - amount
        self._mark_updated()

        transaction = CreditTransaction.create_usage(
            user_id=self._id,
            credits=amount,
            description=reason
        )
        self._transactions.append(transaction)

        return transaction

    def add_credits(
            self,
            amount: Credits,
            price: Money,
            payment_id: str,
            description: str
    ) -> CreditTransaction:
        """Add credits to user account from a purchase."""
        if not payment_id:
            raise ValueError("Payment ID is required for adding credits")

        self._credits = self._credits + amount
        self._total_purchased = self._total_purchased + price
        self._mark_updated()

        transaction = CreditTransaction.create_purchase(
            user_id=self._id,
            credits=amount,
            amount=price,
            payment_id=payment_id,
            description=description
        )
        self._transactions.append(transaction)

        return transaction

    def refund_credits(self, amount: Credits, reason: str) -> CreditTransaction:
        """Refund credits to user (e.g., when generation fails)."""
        self._credits = self._credits + amount
        self._mark_updated()

        transaction = CreditTransaction.create_refund(
            user_id=self._id,
            credits=amount,
            description=reason
        )
        self._transactions.append(transaction)

        return transaction

    def has_sufficient_credits(self, required: Credits) -> bool:
        """Check if user has enough credits for an operation"""
        return self._credits >= required

    def clear_pending_transactions(self) -> None:
        """Clear pending transactions after they've been persisted"""
        self._transactions.clear()

    def _mark_updated(self) -> None:
        """Mark entity as updated"""
        self._updated_at = datetime.now()

    @staticmethod
    def create(email: Email, initial_credits: Credits = None) -> "User":
        """Factory method to create a new user"""
        return User(
            id=None,
            email=email,
            credits=initial_credits or Credits(0),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._id == other._id and self._email == other._email

    def __hash__(self) -> int:
        return hash((self._id, self._email.value))
