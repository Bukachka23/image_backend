from fastapi import APIRouter, Depends

from src.application.use_cases.get_user_credits import GetUserCreditsRequest, GetUserCreditsUseCase
from src.presentation.api.dependencies import get_user_credits_use_case
from src.presentation.api.error_handlers import map_domain_exception_to_http
from src.presentation.api.schemas.responses import CreditsResponse

router = APIRouter(prefix="/api", tags=["credits"])


@router.get("/credits/{email}", response_model=CreditsResponse)
async def get_credits(
        email: str,
        use_case: GetUserCreditsUseCase = Depends(get_user_credits_use_case)
):
    """Get user credit balance"""
    request = GetUserCreditsRequest(email=email)

    result = await use_case.execute(request)

    if result.is_failure():
        raise map_domain_exception_to_http(result.error)

    return CreditsResponse(
        credits=result.value.credits,
        email=result.value.email
    )
