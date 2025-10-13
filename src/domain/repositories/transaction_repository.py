from abc import ABC, abstractmethod

from src.domain.entities.credit_transaction import CreditTransaction


class TransactionRepository(ABC):
    """Repository interface for CreditTransaction entity"""

    @abstractmethod
    async def save(self, transaction: CreditTransaction) -> CreditTransaction:
        """Save a new transaction"""

    @abstractmethod
    async def find_by_user_id(self, user_id: int, limit: int = 50) -> list[CreditTransaction]:
        """Find transactions for a user"""

    @abstractmethod
    async def find_by_payment_id(self, payment_id: str) -> CreditTransaction | None:
        """Find transaction by payment ID"""
