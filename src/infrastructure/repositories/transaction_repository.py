
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities.credit_transaction import CreditTransaction, TransactionType
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.money import Money
from src.infrastructure.database.models import TransactionModel


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository"""

    def __init__(self, session: Session):
        self._session = session

    async def save(self, transaction: CreditTransaction) -> CreditTransaction:
        """Save a new transaction"""
        model = self._to_model(transaction)
        self._session.add(model)

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def find_by_user_id(self, user_id: int, limit: int = 50) -> list[CreditTransaction]:
        """Find transactions for a user"""
        if hasattr(self._session, "execute"):  # Async session
            result = self._session.execute(
                select(TransactionModel)
                .where(TransactionModel.user_id == user_id)
                .order_by(TransactionModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
        else:  # Sync session
            models = (
                self._session.query(TransactionModel)
                .filter(TransactionModel.user_id == user_id)
                .order_by(TransactionModel.created_at.desc())
                .limit(limit)
                .all()
            )

        return [self._to_entity(model) for model in models]

    async def find_by_payment_id(self, payment_id: str) -> CreditTransaction | None:
        """Find transaction by payment ID"""
        if hasattr(self._session, "execute"):  # Async session
            result = self._session.execute(
                select(TransactionModel).where(TransactionModel.stripe_payment_id == payment_id)
            )
            model = result.scalar_one_or_none()
        else:  # Sync session
            model = (
                self._session.query(TransactionModel)
                .filter(TransactionModel.stripe_payment_id == payment_id)
                .first()
            )

        return self._to_entity(model) if model else None

    def _to_entity(self, model: TransactionModel) -> CreditTransaction:
        """Convert ORM model to domain entity"""
        return CreditTransaction(
            id=model.id,
            user_id=model.user_id,
            transaction_type=TransactionType(model.type),
            credits=Credits(model.credits),
            amount=Money(model.amount) if model.amount else None,
            payment_id=model.stripe_payment_id,
            description=model.description,
            created_at=model.created_at
        )

    def _to_model(self, entity: CreditTransaction) -> TransactionModel:
        """Convert domain entity to ORM model"""
        return TransactionModel(
            id=entity.id,
            user_id=entity.user_id,
            stripe_payment_id=entity.payment_id,
            type=entity.transaction_type.value,
            credits=entity.credits.value,
            amount=entity.amount.value if entity.amount else None,
            description=entity.description,
            created_at=entity.created_at
        )
