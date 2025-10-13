from fastapi import APIRouter, Depends

from src.application.use_cases.submit_feedback import SubmitFeedbackRequest as UseCaseFeedbackRequest
from src.application.use_cases.submit_feedback import SubmitFeedbackUseCase
from src.presentation.api.dependencies import get_submit_feedback_use_case
from src.presentation.api.error_handlers import map_domain_exception_to_http
from src.presentation.api.schemas.requests import FeedbackRequest
from src.presentation.api.schemas.responses import FeedbackResponse

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
        request: FeedbackRequest,
        use_case: SubmitFeedbackUseCase = Depends(get_submit_feedback_use_case)
):
    """Submit user feedback"""
    use_case_request = UseCaseFeedbackRequest(
        message=request.message,
        email=request.email
    )

    result = await use_case.execute(use_case_request)

    if result.is_failure():
        raise map_domain_exception_to_http(result.error)

    return FeedbackResponse(ok=result.value.success)
