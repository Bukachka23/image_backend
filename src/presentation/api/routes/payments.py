from fastapi import APIRouter, Depends

from src.application.use_cases.purchase_credits import PurchaseCreditsRequest, PurchaseCreditsUseCase
from src.infrastructure.config.settings import Settings
from src.presentation.api.dependencies import get_app_settings, get_purchase_credits_use_case
from src.presentation.api.error_handlers import map_domain_exception_to_http
from src.presentation.api.schemas.requests import CheckoutRequest
from src.presentation.api.schemas.responses import CheckoutResponse

router = APIRouter(prefix="/api", tags=["payments"])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
        request: CheckoutRequest,
        use_case: PurchaseCreditsUseCase = Depends(get_purchase_credits_use_case),
        settings: Settings = Depends(get_app_settings)
):
    """Create a Stripe checkout session for purchasing credits"""
    use_case_request = PurchaseCreditsRequest(
        email=str(request.email),
        package_key=request.package,
        success_url=f"{settings.frontend_url}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}?payment=cancelled"
    )

    result = await use_case.execute(use_case_request)

    if result.is_failure():
        raise map_domain_exception_to_http(result.error)

    return CheckoutResponse(
        checkout_url=result.value.checkout_url,
        session_id=result.value.session_id
    )
