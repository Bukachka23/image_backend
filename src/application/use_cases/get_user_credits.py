from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email
from src.shared.result import Result, Success


class GetUserCreditsRequest:
    """Request for getting user credits."""

    def __init__(self, email: str):
        self.email = Email(email)


class GetUserCreditsResponse:
    """Response for getting user credits."""

    def __init__(self, email: str, credits: int):
        self.email = email
        self.credits = credits


class GetUserCreditsUseCase:
    """Use case for getting user credits."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, request: GetUserCreditsRequest) -> Result[GetUserCreditsResponse]:
        user = await self._user_repo.find_by_email(request.email)
        if not user:
            from src.domain.entities.user import User
            user = User.create(request.email)
            user = await self._user_repo.save(user)

        return Success(GetUserCreditsResponse(
            email=user.email.value,
            credits=user.credits.value
        ))
