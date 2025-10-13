from abc import ABC, abstractmethod

from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


class CheckoutSession:
    """Represents a payment checkout session"""

    def __init__(self, session_id: str, checkout_url: str):
        self.session_id = session_id
        self.checkout_url = checkout_url


class PaymentGateway(ABC):
    """Interface for payment processing"""

    @abstractmethod
    async def create_customer(self, email: Email) -> str:
        """Create a customer in the payment system. Returns customer ID."""

    @abstractmethod
    async def create_checkout_session(
            self,
            customer_id: str,
            amount: Money,
            product_name: str,
            product_description: str,
            success_url: str,
            cancel_url: str,
            metadata: dict
    ) -> CheckoutSession:
        """Create a checkout session for payment"""

    @abstractmethod
    async def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> dict:
        """Verify webhook signature and return event data"""
