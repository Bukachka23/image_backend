import stripe

from src.domain.exceptions import PaymentProcessingError
from src.domain.services.payment_gateway import CheckoutSession, PaymentGateway
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


class StripePaymentGateway(PaymentGateway):
    """Stripe implementation of PaymentGateway"""

    def __init__(self, api_key: str, webhook_secret: str = None):
        stripe.api_key = api_key
        self._webhook_secret = webhook_secret

    async def create_customer(self, email: Email) -> str:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(email=email.value)
            return customer.id
        except stripe.StripeError as e:
            raise PaymentProcessingError(f"Failed to create Stripe customer: {e!s}")

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
        """Create a Stripe checkout session"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": amount.currency.lower(),
                            "unit_amount": amount.to_cents(),
                            "product_data": {
                                "name": product_name,
                                "description": product_description,
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )

            return CheckoutSession(
                session_id=session.id,
                checkout_url=session.url
            )

        except stripe.StripeError as e:
            raise PaymentProcessingError(f"Failed to create checkout session: {e!s}")

    async def verify_webhook_signature(self, payload: bytes, signature: str, secret: str = None) -> dict:
        """Verify Stripe webhook signature"""
        webhook_secret = secret or self._webhook_secret

        if not webhook_secret:
            raise PaymentProcessingError("Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        except ValueError as e:
            raise PaymentProcessingError(f"Invalid payload: {e!s}")
        except stripe.SignatureVerificationError as e:
            raise PaymentProcessingError(f"Invalid signature: {e!s}")
