from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    """SQLAlchemy User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, index=True, nullable=False)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    credits = Column(Integer, default=0, nullable=False)
    total_purchased = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class TransactionModel(Base):
    """SQLAlchemy Transaction model"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    stripe_payment_id = Column(String(255), unique=True, nullable=True)
    type = Column(String(50), nullable=False)
    credits = Column(Integer, nullable=False)
    amount = Column(Float, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
