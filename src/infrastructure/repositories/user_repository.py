
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: Session):
        self._session = session

    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
        else:
            model = self._session.query(UserModel).filter(UserModel.id == user_id).first()

        return self._to_entity(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(select(UserModel).where(UserModel.email == email.value))
            model = result.scalar_one_or_none()
        else:
            model = self._session.query(UserModel).filter(UserModel.email == email.value).first()

        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        """Save a new user"""
        model = self._to_model(user)
        self._session.add(model)

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def update(self, user: User) -> User:
        """Update an existing user"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            model = result.scalar_one()
        else:
            model = self._session.query(UserModel).filter(UserModel.id == user.id).one()

        model.email = user.email.value
        model.credits = user.credits.value
        model.stripe_customer_id = user.stripe_customer_id
        model.total_purchased = user.total_purchased.value
        model.updated_at = user.updated_at

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel.id).where(UserModel.email == email.value)
            )
            return result.scalar_one_or_none() is not None
        return self._session.query(UserModel.id).filter(UserModel.email == email.value).first() is not None

    def _to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity"""
        return User(
            id=model.id,
            email=Email(model.email),
            credits=Credits(model.credits),
            stripe_customer_id=model.stripe_customer_id,
            total_purchased=Money(model.total_purchased),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to ORM model"""
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            credits=entity.credits.value,
            stripe_customer_id=entity.stripe_customer_id,
            total_purchased=entity.total_purchased.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
