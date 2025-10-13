from fastapi import APIRouter, Depends, Header, Request

from src.application.use_cases.complete_payment import CompletePaymentRequest, CompletePaymentUseCase
from src.infrastructure.config.settings import Settings
from src.infrastructure.external_services.stripe_payment_gateway import StripePaymentGateway
from src.presentation.api.dependencies import (
    get_app_settings,
    get_complete_payment_use_case,
    get_payment_gateway,
)
from src.presentation.api.error_handlers import map_domain_exception_to_http
from src.presentation.api.schemas.responses import WebhookResponse

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/stripe", response_model=WebhookResponse)
async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None, alias="stripe-signature"),
        payment_gateway: StripePaymentGateway = Depends(get_payment_gateway),
        use_case: CompletePaymentUseCase = Depends(get_complete_payment_use_case),
        settings: Settings = Depends(get_app_settings)
):
    """Handle Stripe webhook events"""
    payload = await request.body()

    try:
        # Verify webhook signature
        event = await payment_gateway.verify_webhook_signature(
            payload=payload,
            signature=stripe_signature,
            secret=settings.stripe_webhook_secret
        )

        # Handle checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # Extract metadata
            user_email = session["metadata"].get("user_email")
            package = session["metadata"].get("package")
            credits = session["metadata"].get("credits")

            if user_email and package and credits:
                use_case_request = CompletePaymentRequest(
                    email=user_email,
                    package_key=package,
                    credits=int(credits),
                    session_id=session["id"]
                )

                result = await use_case.execute(use_case_request)

                if result.is_failure():
                    print(f"Failed to complete payment: {result.error}")
                else:
                    print(f"Credits added: {user_email} +{credits} credits")

        return WebhookResponse(status="success")

    except Exception as e:
        print(f"Webhook error: {e!s}")
        raise map_domain_exception_to_http(e)
