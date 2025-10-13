from fastapi import HTTPException, status

from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainException,
    ImageGenerationError,
    InsufficientCreditsError,
    InvalidCreditPackageError,
    InvalidEmailError,
    PaymentProcessingError,
    UserNotFoundError,
)


def map_domain_exception_to_http(exception: Exception) -> HTTPException:
    """Map domain exceptions to HTTP exceptions"""
    if isinstance(exception, InsufficientCreditsError):
        return HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exception)
        )

    if isinstance(exception, UserNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception)
        )

    if isinstance(exception, InvalidEmailError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    if isinstance(exception, InvalidCreditPackageError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    if isinstance(exception, ImageGenerationError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {exception!s}"
        )

    if isinstance(exception, PaymentProcessingError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {exception!s}"
        )

    if isinstance(exception, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exception)
        )

    if isinstance(exception, AuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exception)
        )

    if isinstance(exception, DomainException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    # Generic exception
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )
