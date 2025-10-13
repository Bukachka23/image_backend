from abc import ABC, abstractmethod

from src.domain.entities.user import User
from src.domain.value_objects.email import Email


class UserRepository(ABC):
    """Repository interface for User aggregate"""

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID"""

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a new user"""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user"""

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
