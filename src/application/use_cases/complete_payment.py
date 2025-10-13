from src.domain.exceptions import UserNotFoundError
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.shared.result import Failure, Result, Success


class CompletePaymentRequest:
    """Request for complete payment."""

    def __init__(self, email: str, package_key: str, credits: int, session_id: str) -> None:
        self.email = Email(email)
        self.package_key = package_key
        self.credits = Credits(credits)
        self.session_id = session_id


class CompletePaymentResponse:
    """Response for complete payment."""

    def __init__(self, credits_added: int, total_credits: int) -> None:
        self.credits_added = credits_added
        self.total_credits = total_credits


class CompletePaymentUseCase:
    """Use case for complete payment."""

    def __init__(self, user_repo: UserRepository, transaction_repo: TransactionRepository) -> None:
        self._user_repo = user_repo
        self._transaction_repo = transaction_repo

    async def execute(self, request: CompletePaymentRequest) -> Result[CompletePaymentResponse]:
        user = await self._user_repo.find_by_email(request.email)
        if not user:
            return Failure(UserNotFoundError(f"User {request.email} not found"))

        from src.application.use_cases.purchase_credits import PurchaseCreditsUseCase
        package = PurchaseCreditsUseCase.PACKAGES.get(request.package_key)
        if not package:
            return Failure(Exception(f"Invalid package: {request.package_key}"))

        transaction = user.add_credits(
            amount=request.credits,
            price=package.price,
            payment_id=request.session_id,
            description=f"Purchase: {package.name}"
        )

        await self._user_repo.update(user)
        await self._transaction_repo.save(transaction)
        user.clear_pending_transactions()

        return Success(CompletePaymentResponse(
            credits_added=request.credits.value,
            total_credits=user.credits.value
        ))
