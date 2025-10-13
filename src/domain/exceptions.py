class DomainException(Exception):
    """Base exception for domain errors"""


class InsufficientCreditsError(DomainException):
    """Raised when user doesn't have enough credits"""


class UserNotFoundError(DomainException):
    """Raised when user cannot be found"""


class InvalidEmailError(DomainException):
    """Raised when email validation fails"""


class InvalidCreditPackageError(DomainException):
    """Raised when an invalid credit package is requested"""


class ImageGenerationError(DomainException):
    """Raised when image generation fails"""


class PaymentProcessingError(DomainException):
    """Raised when payment processing fails"""


class AuthenticationError(DomainException):
    """Raised when authentication fails"""


class AuthorizationError(DomainException):
    """Raised when user is not authorized for an action"""
