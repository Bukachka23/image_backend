from src.domain.value_objects.email import Email
from src.shared.result import Failure, Result, Success


class SubmitFeedbackRequest:
    """Request for submitting user feedback."""

    def __init__(self, message: str, email: str = None) -> None:
        self.message = message.strip()
        self.email = Email(email) if email else None


class SubmitFeedbackResponse:
    """Response for submitting user feedback."""

    def __init__(self, success: bool) -> None:
        self.success = success


class SubmitFeedbackUseCase:
    """Use case for submitting user feedback."""

    async def execute(self, request: SubmitFeedbackRequest) -> Result[SubmitFeedbackResponse]:
        if not request.message:
            return Failure(ValueError("Feedback message cannot be empty"))

        email_str = request.email.value if request.email else "anonymous"
        print(f"[FEEDBACK] from={email_str} :: {request.message[:500]}")

        return Success(SubmitFeedbackResponse(success=True))
