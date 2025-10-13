from src.domain.exceptions import InvalidCreditPackageError, PaymentProcessingError
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.payment_gateway import PaymentGateway
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.shared.result import Failure, Result, Success


class CreditPackage:
    """Represents a credit package offering"""

    def __init__(self, key: str, credits: int, price: float, name: str) -> None:
        self.key = key
        self.credits = Credits(credits)
        self.price = Money(price)
        self.name = name


class PurchaseCreditsRequest:
    """Request for purchasing credits."""

    def __init__(self, email: str, package_key: str, success_url: str, cancel_url: str) -> None:
        self.email = Email(email)
        self.package_key = package_key
        self.success_url = success_url
        self.cancel_url = cancel_url


class PurchaseCreditsResponse:
    """Response for purchasing credits."""

    def __init__(self, checkout_url: str, session_id: str) -> None:
        self.checkout_url = checkout_url
        self.session_id = session_id


class PurchaseCreditsUseCase:
    """Use case for purchasing credits."""

    PACKAGES = {
        "starter": CreditPackage("starter", 10, 9.99, "Starter Pack"),
        "pro": CreditPackage("pro", 50, 39.99, "Pro Pack"),
        "business": CreditPackage("business", 150, 99.99, "Business Pack"),
    }

    def __init__(
            self,
            user_repo: UserRepository,
            payment_gateway: PaymentGateway
    ) -> None:
        self._user_repo = user_repo
        self._payment_gateway = payment_gateway

    async def execute(self, request: PurchaseCreditsRequest) -> Result[PurchaseCreditsResponse]:
        # Validate package
        package = self.PACKAGES.get(request.package_key)
        if not package:
            return Failure(InvalidCreditPackageError(f"Invalid package: {request.package_key}"))

        # Get or create user
        user = await self._user_repo.find_by_email(request.email)
        if not user:
            from src.domain.entities.user import User
            user = User.create(request.email)
            user = await self._user_repo.save(user)

        # Create Stripe customer if needed
        if not user.stripe_customer_id:
            try:
                customer_id = await self._payment_gateway.create_customer(request.email)
                user.set_stripe_customer_id(customer_id)
                await self._user_repo.update(user)
            except Exception as e:
                return Failure(PaymentProcessingError(f"Failed to create customer: {e!s}"))

        # Create checkout session
        try:
            session = await self._payment_gateway.create_checkout_session(
                customer_id=user.stripe_customer_id,
                amount=package.price,
                product_name=package.name,
                product_description=f"{package.credits.value} credits for AI photo generation",
                success_url=request.success_url,
                cancel_url=request.cancel_url,
                metadata={
                    "user_email": request.email.value,
                    "package": package.key,
                    "credits": str(package.credits.value),
                }
            )

            return Success(PurchaseCreditsResponse(
                checkout_url=session.checkout_url,
                session_id=session.session_id
            ))

        except Exception as e:
            return Failure(PaymentProcessingError(f"Failed to create checkout: {e!s}"))
