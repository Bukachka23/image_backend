from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.use_cases.complete_payment import CompletePaymentUseCase
from src.application.use_cases.generate_image import GenerateImageUseCase
from src.application.use_cases.get_user_credits import GetUserCreditsUseCase
from src.application.use_cases.purchase_credits import PurchaseCreditsUseCase
from src.application.use_cases.submit_feedback import SubmitFeedbackUseCase
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.database.connection import get_database
from src.infrastructure.external_services.gemini_image_generator import GeminiImageGenerator
from src.infrastructure.external_services.stripe_payment_gateway import StripePaymentGateway
from src.infrastructure.repositories import SQLAlchemyTransactionRepository, SQLAlchemyUserRepository


async def get_db_session() -> AsyncGenerator[Session, None]:
    """Get database session"""
    db = get_database()
    async with db.get_session() as session:
        yield session


def get_app_settings() -> Settings:
    """Get application settings"""
    return get_settings()


def get_user_repository(session: Session = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    """Get user repository"""
    return SQLAlchemyUserRepository(session)


def get_transaction_repository(session: Session = Depends(get_db_session)) -> SQLAlchemyTransactionRepository:
    """Get transaction repository"""
    return SQLAlchemyTransactionRepository(session)


def get_image_generator(settings: Settings = Depends(get_app_settings)) -> GeminiImageGenerator:
    """Get image generator service"""
    return GeminiImageGenerator(api_key=settings.gemini_api_key)


def get_payment_gateway(settings: Settings = Depends(get_app_settings)) -> StripePaymentGateway:
    """Get payment gateway service"""
    return StripePaymentGateway(
        api_key=settings.stripe_secret_key,
        webhook_secret=settings.stripe_webhook_secret
    )


def get_generate_image_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    image_generator: GeminiImageGenerator = Depends(get_image_generator)
) -> GenerateImageUseCase:
    """Get generate image use case"""
    return GenerateImageUseCase(user_repo, transaction_repo, image_generator)


def get_purchase_credits_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    payment_gateway: StripePaymentGateway = Depends(get_payment_gateway)
) -> PurchaseCreditsUseCase:
    """Get purchase credits use case"""
    return PurchaseCreditsUseCase(user_repo, payment_gateway)


def get_complete_payment_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository)
) -> CompletePaymentUseCase:
    """Get complete payment use case"""
    return CompletePaymentUseCase(user_repo, transaction_repo)


def get_user_credits_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetUserCreditsUseCase:
    """Get user credits use case"""
    return GetUserCreditsUseCase(user_repo)


def get_submit_feedback_use_case() -> SubmitFeedbackUseCase:
    """Get submit feedback use case"""
    return SubmitFeedbackUseCase()
