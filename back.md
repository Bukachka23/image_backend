Project Path: image_backend

Source Tree:

```txt
image_backend
├── Dockerfile
├── Makefile
├── README.md
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── application
│   │   ├── __init__.py
│   │   └── use_cases
│   │       ├── __init__.py
│   │       ├── complete_payment.py
│   │       ├── generate_image.py
│   │       ├── get_user_credits.py
│   │       ├── purchase_credits.py
│   │       └── submit_feedback.py
│   ├── domain
│   │   ├── __init__.py
│   │   ├── entities
│   │   │   ├── __init__.py
│   │   │   ├── credit_transaction.py
│   │   │   └── user.py
│   │   ├── exceptions.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── transaction_repository.py
│   │   │   └── user_repository.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── image_generator.py
│   │   │   └── payment_gateway.py
│   │   └── value_objects
│   │       ├── __init__.py
│   │       ├── credits.py
│   │       ├── email.py
│   │       └── money.py
│   ├── infrastructure
│   │   ├── __init__.py
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── database
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   ├── external_services
│   │   │   ├── __init__.py
│   │   │   ├── gemini_image_generator.py
│   │   │   └── stripe_payment_gateway.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       ├── transaction_repository.py
│   │       └── user_repository.py
│   ├── main.py
│   ├── presentation
│   │   ├── __init__.py
│   │   └── api
│   │       ├── __init__.py
│   │       ├── dependencies.py
│   │       ├── error_handlers.py
│   │       ├── routes
│   │       │   ├── __init__.py
│   │       │   ├── credits.py
│   │       │   ├── feedback.py
│   │       │   ├── health.py
│   │       │   ├── image_generation.py
│   │       │   ├── payments.py
│   │       │   └── webhooks.py
│   │       └── schemas
│   │           ├── __init__.py
│   │           ├── requests.py
│   │           └── responses.py
│   └── shared
│       ├── __init__.py
│       └── result.py
└── tests

```

`image_backend/Dockerfile`:

```
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Set Python to be unbuffered (see output immediately)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

# CRITICAL: Bind to 0.0.0.0 to accept connections from Railway's internal network
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "600"]

```

`image_backend/Makefile`:

```
APP_NAME = h2l_agent_caller

.PHONY: clean help

help:
	clear;
	@echo "================= Usage =================";
	@echo "build                        : Rebuild app container.";
	@echo "run                          : Run service standalone.";
	@echo "stop                         : Stop and keep all containers.";
	@echo "clean-pyc                    : Remove python artifacts.";
	@echo "clean-build                  : Remove build artifacts.";
	@echo "clean                        : Complex cleaning. Clean the folder from build/test related folders and orphans.";
	@echo "ruff_check                   : Run lint check using ruff.";
	@echo "ruff_fix                     : Run lint errors fixing using ruff (pls, use with caution)";
	@echo "ruff_format                  : Run code formatting using ruff (pls, use with caution).";

### APP LOCAL BUILDING AND RUNNING
## Rebuild app container.
build:
	@docker network create localai || true
	@docker compose build $(APP_NAME)

## Run service standalone.
run: build
	rm -f celerybeat.pid
	@docker compose up


### CLEANING AND STOPPING
## Stop and keep all containers.
stop:
	@docker compose stop $(docker ps -aq)

## Remove python artifacts.
clean-pyc:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +

## Remove build artifacts.
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

## Complex cleaning. Clean the folder from build/test related folders and orphans.
clean: clean-build clean-pyc
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -f .coverage
	@docker compose down --remove-orphans


### LINTERS, OTHER CHECKS AND AUTO FORMATTING
## Run lint check using ruff.
ruff_check:
	@echo "\033[0;32mLINT CHECK WITH RUFF COMMENCED\033[0m"
	@ruff check || true
	@echo "\033[0;31mLINT CHECK WITH RUFF COMPLETED\033[0m"

## Run lint errors fixing using ruff (pls, use with caution)
ruff_fix:
	@echo "\033[0;32mFIXING WITH RUFF COMMENCED\033[0m"
	@ruff check --fix || true
	@echo "\033[0;31mFIXING WITH RUFF COMPLETED\033[0m"

## Run code formatting using ruff (pls, use with caution)
ruff_format:
	@echo "\033[0;32mFORMATTING WITH RUFF COMMENCED\033[0m"
	@ruff format . --check || true
	@ruff format || true
	@echo "\033[0;31mFORMATTING WITH RUFF COMPLETED. PLS USE make diff TO CHECK CHANGES\033[0m"

## Check all changes in current commit (prefer to use after any authomatic fixes and formatting)
diff:
	@git diff

```

`image_backend/pyproject.toml`:

```toml
[project]
name = "gsigner-service"
requires-python = "==3.11.4"

[tool.setuptools]
packages = ["src"]

[tool.ruff]
line-length = 120
exclude = [
    "alembic/*",  # Ignore all Python files in the alembic directory and its subdirectories
]
preview = true

[tool.ruff.lint]
# https://docs.astral.sh/ruff/rules/  - to check error codes
select = [
    "F",  # pyflakes
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "I",  # isort
    "N",  # pep8-naming
    "D",  # pydocstyle
    "UP",  # pyupgrade
    "ANN",  # flake8-annotations
    "ASYNC",  # flake8-async
    "S",  # flake8-bandit
    "BLE",  # flake8-blind-except
    "B",  # flake8-bugbear
    "A",  # flake8-builtins
    "COM", # flake8-commas
    "C4",  # flake8-comprehensions
    "EM",  # flake8-errmsg
    "ISC",  # flake8-implicit-str-concat
    "ICN",  # flake8-import-conventions
    "LOG",  # flake8-logging
    "G",  # flake8-logging-format
    "PIE", # flake8-pie
    "T20",  # flake8-print
    "PT",  # flake8-pytest-style
    "Q",  # flake8-quotes
    "RSE",  # flake8-raise
    "RET",  # flake8-return
    "SLF",  # flake8-self
    "SLOT",  # flake8-slots
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "INT",  # flake8-gettext
    "ARG",  # flake8-unused-arguments
    "TD",  # flake8-todos
#    "ERA",  # eradicate
    "PL",  # Pylint
    "FLY",  # flyint
    "FAST",  # FastAPI
    "PERF",  # Perflint
    "FURB",  # refurb
    "RUF",  # Ruff-specific rules
]
ignore = [
    "N805",  # First argument of a method should be named `self`

    "D100",  # Missing docstring in public module
    "D101",  # Missing docstring in public class
    "D102",  # Missing docstring in public method
    "D103",  # Missing docstring in public function
    "D104",  # Missing docstring in public package
    "D105",  # Missing docstring in magic method
    "D106",  # Missing docstring in public nested class
    "D107",  # Missing docstring in __init__
    "D203",  # 1 blank line required before class docstring
    "D212",  # Multi-line docstring summary should start at the first line
    "D401",  # First line of docstring should be in imperative mood: "{first_line}"

    "COM812",  # Trailing comma missing

    "G004",  # Logging statement uses f-string

    "ANN002",  # Missing type annotation for args
    "ANN003",  # Missing type annotation for kwargs
    "ANN101",  # Missing type annotation for self in method
    "ANN102",  # Missing type annotation for cls in classmethod

    "ISC001",  # Implicitly concatenated string literals on one line

    "TD003",  # Missing issue link on the line following this TO DO

    "PLR0904",  # Too many public methods (21 > 20)
    "PLR0913",  # Too many arguments in function definition
    "PLR0917",  # Too many positional arguments

    "FAST001",  # FastAPI route with redundant response_model argument

    "RUF012",  # Mutable class attributes should be annotated with `typing.ClassVar`
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = [
    "S",  # Bandit checks in tests
    "ANN",  # Annotations in tests
    "ARG",  # Unused arguments in tests
    "TD",  # TO DO in tests
    "PL",  # Pylint in tests
    "RUF",  # Ruff-specific rules in tests
]

[tool.ruff.format]
docstring-code-format = true
indent-style = "space"
quote-style = "double"


```

`image_backend/src/application/use_cases/__init__.py`:

```py
from src.application.use_cases.complete_payment import (
    CompletePaymentRequest,
    CompletePaymentResponse,
    CompletePaymentUseCase,
)
from src.application.use_cases.generate_image import (
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateImageUseCase,
)
from src.application.use_cases.get_user_credits import (
    GetUserCreditsRequest,
    GetUserCreditsResponse,
    GetUserCreditsUseCase,
)
from src.application.use_cases.purchase_credits import (
    PurchaseCreditsRequest,
    PurchaseCreditsResponse,
    PurchaseCreditsUseCase,
)
from src.application.use_cases.submit_feedback import (
    SubmitFeedbackRequest,
    SubmitFeedbackResponse,
    SubmitFeedbackUseCase,
)

__all__ = [
    "CompletePaymentRequest",
    "CompletePaymentResponse",
    "CompletePaymentUseCase",
    "GenerateImageRequest",
    "GenerateImageResponse",
    "GenerateImageUseCase",
    "GetUserCreditsRequest",
    "GetUserCreditsResponse",
    "GetUserCreditsUseCase",
    "PurchaseCreditsRequest",
    "PurchaseCreditsResponse",
    "PurchaseCreditsUseCase",
    "SubmitFeedbackRequest",
    "SubmitFeedbackResponse",
    "SubmitFeedbackUseCase",
]

```

`image_backend/src/application/use_cases/complete_payment.py`:

```py
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

```

`image_backend/src/application/use_cases/generate_image.py`:

```py

from PIL import Image

from src.domain.exceptions import ImageGenerationError, InsufficientCreditsError, UserNotFoundError
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.image_generator import GenerationRequest, ImageGenerator
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.shared.result import Failure, Result, Success


class GenerateImageRequest:
    """Request for image generation."""

    def __init__(self, email: str, prompt: str, image: Image.Image, transformation_mode: str) -> None:
        self.email = Email(email)
        self.prompt = prompt
        self.image = image
        self.transformation_mode = transformation_mode


class GenerateImageResponse:
    """Response for image generation."""

    def __init__(self, images: list[str], credits_remaining: int) -> None:
        self.images = images
        self.credits_remaining = credits_remaining


class GenerateImageUseCase:
    """Use case for image generation."""

    CREDITS_PER_GENERATION = Credits(3)

    def __init__(
            self,
            user_repo: UserRepository,
            transaction_repo: TransactionRepository,
            image_generator: ImageGenerator
    ) -> None:
        self._user_repo = user_repo
        self._transaction_repo = transaction_repo
        self._image_generator = image_generator

    async def execute(self, request: GenerateImageRequest) -> Result[GenerateImageResponse]:
        user = await self._user_repo.find_by_email(request.email)
        if not user:
            return Failure(UserNotFoundError(f"User with email {request.email} not found"))

        if not user.has_sufficient_credits(self.CREDITS_PER_GENERATION):
            return Failure(InsufficientCreditsError(
                f"Need {self.CREDITS_PER_GENERATION.value} credits, have {user.credits.value}"
            ))

        try:
            transaction = user.deduct_credits(
                self.CREDITS_PER_GENERATION,
                "Image generation (3 variations)"
            )

            # Save user and transaction
            await self._user_repo.update(user)
            await self._transaction_repo.save(transaction)
            user.clear_pending_transactions()

            # Generate prompt based on mode
            generation_prompt = self._build_generation_prompt(
                request.prompt,
                request.transformation_mode
            )

            # Generate images
            gen_request = GenerationRequest(
                prompt=generation_prompt,
                reference_image=request.image,
                variations=3
            )

            images = await self._image_generator.generate(gen_request)

            if not images:
                refund_tx = user.refund_credits(
                    self.CREDITS_PER_GENERATION,
                    "Generation failed - no images produced"
                )
                await self._user_repo.update(user)
                await self._transaction_repo.save(refund_tx)
                user.clear_pending_transactions()

                return Failure(ImageGenerationError("Failed to generate any images"))

            return Success(GenerateImageResponse(
                images=images,
                credits_remaining=user.credits.value
            ))

        except Exception as e:
            refund_tx = user.refund_credits(
                self.CREDITS_PER_GENERATION,
                f"Error during generation: {str(e)[:100]}"
            )
            await self._user_repo.update(user)
            await self._transaction_repo.save(refund_tx)
            user.clear_pending_transactions()

            return Failure(ImageGenerationError(str(e)))

    def _build_generation_prompt(self, prompt: str, mode: str) -> str:
        """Build the AI generation prompt based on transformation mode"""
        if mode == "item-only" or "Same person, same pose" in prompt:
            if "only change to" in prompt:
                style = prompt.split("only change to")[1].strip().strip(".")
            else:
                style = prompt.partition("style of")[2].strip().strip(".")

            return (
                f"Create a highly realistic, photographic image. Keep the exact same person, pose, and photo composition. "
                f"Only change the clothing/outfit to '{style}' style. "
                f"Maintain facial features, body position, and background exactly as they are. "
                f"Use natural lighting, realistic skin texture, and professional photography quality. "
                f"Ensure the clothing looks authentic and properly fitted to the person's body."
            )
        style = prompt.partition("style of")[2].strip().strip(".")
        return (
            f"Create a highly realistic, professional photograph of this person in a '{style}' theme. "
            f"Transform the entire scene with an appropriate background, natural pose, and authentic outfit "
            f"that reflects '{style}' style. Use photographic quality with natural lighting, "
            f"realistic skin texture, proper shadows, and lifelike details. "
            f"Ensure the image looks like it was taken with a professional camera, not AI-generated."
        )

```

`image_backend/src/application/use_cases/get_user_credits.py`:

```py
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

```

`image_backend/src/application/use_cases/purchase_credits.py`:

```py
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

```

`image_backend/src/application/use_cases/submit_feedback.py`:

```py
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

```

`image_backend/src/domain/entities/credit_transaction.py`:

```py
from datetime import datetime
from enum import Enum

from src.domain.value_objects.credits import Credits
from src.domain.value_objects.money import Money


class TransactionType(Enum):
    """Types of credit transactions"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"


class CreditTransaction:
    """Entity representing a credit transaction"""

    def __init__(
            self,
            id: int | None,
            user_id: int,
            transaction_type: TransactionType,
            credits: Credits,
            amount: Money | None = None,
            payment_id: str | None = None,
            description: str | None = None,
            created_at: datetime | None = None
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._type = transaction_type
        self._credits = credits
        self._amount = amount
        self._payment_id = payment_id
        self._description = description
        self._created_at = created_at or datetime.now()

        self._validate()

    def _validate(self) -> None:
        """Validate transaction invariants"""
        if self._type == TransactionType.PURCHASE and not self._payment_id:
            raise ValueError("Purchase transactions must have a payment ID")

        if self._type == TransactionType.PURCHASE and not self._amount:
            raise ValueError("Purchase transactions must have an amount")

        if self._type == TransactionType.USAGE and self._credits.value > 0:
            raise ValueError("Usage transactions must have negative credits")

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def transaction_type(self) -> TransactionType:
        return self._type

    @property
    def credits(self) -> Credits:
        return self._credits

    @property
    def amount(self) -> Money | None:
        return self._amount

    @property
    def payment_id(self) -> str | None:
        return self._payment_id

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @staticmethod
    def create_purchase(
            user_id: int,
            credits: Credits,
            amount: Money,
            payment_id: str,
            description: str
    ) -> "CreditTransaction":
        """Factory method for purchase transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.PURCHASE,
            credits=credits,
            amount=amount,
            payment_id=payment_id,
            description=description
        )

    @staticmethod
    def create_usage(
            user_id: int,
            credits: Credits,
            description: str
    ) -> "CreditTransaction":
        """Factory method for usage transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.USAGE,
            credits=Credits(-abs(credits.value)),
            description=description
        )

    @staticmethod
    def create_refund(
            user_id: int,
            credits: Credits,
            description: str
    ) -> "CreditTransaction":
        """Factory method for refund transactions"""
        return CreditTransaction(
            id=None,
            user_id=user_id,
            transaction_type=TransactionType.REFUND,
            credits=credits,
            description=description
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, CreditTransaction):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

```

`image_backend/src/domain/entities/user.py`:

```py
from datetime import datetime

from src.domain.entities.credit_transaction import CreditTransaction
from src.domain.exceptions import InsufficientCreditsError
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


class User:
    """User aggregate root - encapsulates all business logic related to users"""

    def __init__(
            self,
            id: int | None,
            email: Email,
            credits: Credits,
            stripe_customer_id: str | None = None,
            total_purchased: Money = None,
            created_at: datetime | None = None,
            updated_at: datetime | None = None
    ) -> None:
        self._id = id
        self._email = email
        self._credits = credits
        self._stripe_customer_id = stripe_customer_id
        self._total_purchased = total_purchased or Money(0.0)
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
        self._transactions: list[CreditTransaction] = []

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def credits(self) -> Credits:
        return self._credits

    @property
    def stripe_customer_id(self) -> str | None:
        return self._stripe_customer_id

    @property
    def total_purchased(self) -> Money:
        return self._total_purchased

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def pending_transactions(self) -> list[CreditTransaction]:
        return self._transactions.copy()

    def set_stripe_customer_id(self, customer_id: str) -> None:
        """Set the Stripe customer ID for payment processing"""
        if not customer_id:
            raise ValueError("Stripe customer ID cannot be empty")
        self._stripe_customer_id = customer_id
        self._mark_updated()

    def deduct_credits(self, amount: Credits, reason: str) -> CreditTransaction:
        """Deduct credits from user account."""
        if self._credits < amount:
            raise InsufficientCreditsError(
                f"Insufficient credits. Required: {amount.value}, Available: {self._credits.value}"
            )

        self._credits = self._credits - amount
        self._mark_updated()

        transaction = CreditTransaction.create_usage(
            user_id=self._id,
            credits=amount,
            description=reason
        )
        self._transactions.append(transaction)

        return transaction

    def add_credits(
            self,
            amount: Credits,
            price: Money,
            payment_id: str,
            description: str
    ) -> CreditTransaction:
        """Add credits to user account from a purchase."""
        if not payment_id:
            raise ValueError("Payment ID is required for adding credits")

        self._credits = self._credits + amount
        self._total_purchased = self._total_purchased + price
        self._mark_updated()

        transaction = CreditTransaction.create_purchase(
            user_id=self._id,
            credits=amount,
            amount=price,
            payment_id=payment_id,
            description=description
        )
        self._transactions.append(transaction)

        return transaction

    def refund_credits(self, amount: Credits, reason: str) -> CreditTransaction:
        """Refund credits to user (e.g., when generation fails)."""
        self._credits = self._credits + amount
        self._mark_updated()

        transaction = CreditTransaction.create_refund(
            user_id=self._id,
            credits=amount,
            description=reason
        )
        self._transactions.append(transaction)

        return transaction

    def has_sufficient_credits(self, required: Credits) -> bool:
        """Check if user has enough credits for an operation"""
        return self._credits >= required

    def clear_pending_transactions(self) -> None:
        """Clear pending transactions after they've been persisted"""
        self._transactions.clear()

    def _mark_updated(self) -> None:
        """Mark entity as updated"""
        self._updated_at = datetime.now()

    @staticmethod
    def create(email: Email, initial_credits: Credits = None) -> "User":
        """Factory method to create a new user"""
        return User(
            id=None,
            email=email,
            credits=initial_credits or Credits(0),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._id == other._id and self._email == other._email

    def __hash__(self) -> int:
        return hash((self._id, self._email.value))

```

`image_backend/src/domain/exceptions.py`:

```py
class DomainException(Exception):
    """Base exception for domain errors"""


class InsufficientCreditsError(DomainException):
    """Raised when user doesn't have enough credits"""


class UserNotFoundError(DomainException):
    """Raised when user cannot be found"""


class InvalidEmailError(DomainException):
    """Raised when email validation fails"""


class InvalidCreditPackageError(DomainException):
    """Raised when an invalid credit package is requested"""


class ImageGenerationError(DomainException):
    """Raised when image generation fails"""


class PaymentProcessingError(DomainException):
    """Raised when payment processing fails"""


class AuthenticationError(DomainException):
    """Raised when authentication fails"""


class AuthorizationError(DomainException):
    """Raised when user is not authorized for an action"""

```

`image_backend/src/domain/repositories/__init__.py`:

```py
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository

__all__ = ["TransactionRepository", "UserRepository"]

```

`image_backend/src/domain/repositories/transaction_repository.py`:

```py
from abc import ABC, abstractmethod

from src.domain.entities.credit_transaction import CreditTransaction


class TransactionRepository(ABC):
    """Repository interface for CreditTransaction entity"""

    @abstractmethod
    async def save(self, transaction: CreditTransaction) -> CreditTransaction:
        """Save a new transaction"""

    @abstractmethod
    async def find_by_user_id(self, user_id: int, limit: int = 50) -> list[CreditTransaction]:
        """Find transactions for a user"""

    @abstractmethod
    async def find_by_payment_id(self, payment_id: str) -> CreditTransaction | None:
        """Find transaction by payment ID"""

```

`image_backend/src/domain/repositories/user_repository.py`:

```py
from abc import ABC, abstractmethod

from src.domain.entities.user import User
from src.domain.value_objects.email import Email


class UserRepository(ABC):
    """Repository interface for User aggregate"""

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID"""

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a new user"""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user"""

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""

```

`image_backend/src/domain/services/__init__.py`:

```py
from src.domain.services.image_generator import GenerationRequest, ImageGenerator
from src.domain.services.payment_gateway import CheckoutSession, PaymentGateway

__all__ = ["CheckoutSession", "GenerationRequest", "ImageGenerator", "PaymentGateway"]

```

`image_backend/src/domain/services/image_generator.py`:

```py
from abc import ABC, abstractmethod

from PIL import Image


class GenerationRequest:
    """Request for image generation"""

    def __init__(self, prompt: str, reference_image: Image.Image, variations: int = 3):
        self.prompt = prompt
        self.reference_image = reference_image
        self.variations = variations


class ImageGenerator(ABC):
    """Interface for AI image generation service"""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> list[str]:
        """Generate images based on prompt and reference image."""

```

`image_backend/src/domain/services/payment_gateway.py`:

```py
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

```

`image_backend/src/domain/value_objects/__init__.py`:

```py
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money

__all__ = ["Credits", "Email", "Money"]

```

`image_backend/src/domain/value_objects/credits.py`:

```py
from typing import Any


class Credits:
    """Credits value object representing user credits"""

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Credits must be an integer")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __add__(self, other: "Credits") -> "Credits":
        if not isinstance(other, Credits):
            raise TypeError("Can only add Credits to Credits")
        return Credits(self._value + other._value)

    def __sub__(self, other: "Credits") -> "Credits":
        if not isinstance(other, Credits):
            raise TypeError("Can only subtract Credits from Credits")
        return Credits(self._value - other._value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Credits):
            return False
        return self._value == other._value

    def __lt__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value < other._value

    def __le__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value <= other._value

    def __gt__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value > other._value

    def __ge__(self, other: "Credits") -> bool:
        if not isinstance(other, Credits):
            raise TypeError("Can only compare Credits with Credits")
        return self._value >= other._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Credits({self._value})"

    def __hash__(self) -> int:
        return hash(self._value)

```

`image_backend/src/domain/value_objects/email.py`:

```py
import re
from typing import Any


class Email:
    """Email value object with validation"""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, value: str):
        self._value = self._validate_and_normalize(value)

    def _validate_and_normalize(self, value: str) -> str:
        if not value:
            raise ValueError("Email cannot be empty")

        normalized = value.strip().lower()

        if not self.EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email format: {value}")

        if len(normalized) > 254:  # RFC 5321
            raise ValueError("Email exceeds maximum length")

        return normalized

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email('{self._value}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Email):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

```

`image_backend/src/domain/value_objects/money.py`:

```py
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


class Money:
    """Money value object for handling currency"""

    def __init__(self, value: float, currency: str = "USD"):
        if value < 0:
            raise ValueError("Money cannot be negative")

        self._value = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self._currency = currency.upper()

    @property
    def value(self) -> float:
        return float(self._value)

    @property
    def currency(self) -> str:
        return self._currency

    def to_cents(self) -> int:
        """Convert to cents for payment processing"""
        return int(self._value * 100)

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self._currency != other._currency:
            raise ValueError("Cannot add different currencies")
        return Money(float(self._value + other._value), self._currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self._currency != other._currency:
            raise ValueError("Cannot subtract different currencies")
        result = float(self._value - other._value)
        if result < 0:
            raise ValueError("Money cannot be negative")
        return Money(result, self._currency)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self._value == other._value and self._currency == other._currency

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self._currency != other._currency:
            raise ValueError("Cannot compare different currencies")
        return self._value < other._value

    def __str__(self) -> str:
        return f"{self._currency} {self._value}"

    def __repr__(self) -> str:
        return f"Money({float(self._value)}, '{self._currency}')"

    def __hash__(self) -> int:
        return hash((self._value, self._currency))

```

`image_backend/src/infrastructure/config/settings.py`:

```py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    gemini_api_key: str | None = None
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    # Database
    database_url: str = "sqlite:///./credits.db"

    # URLs
    frontend_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] = ["*"]

    # Business Rules
    credits_per_generation: int = 3

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment
    environment: str = "development"
    debug: bool = False

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def initialize_settings() -> Settings:
    """Initialize settings (useful for testing)"""
    global _settings
    _settings = Settings()
    return _settings

```

`image_backend/src/infrastructure/database/connection.py`:

```py
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseConnection:
    """Manages database connection and sessions"""

    def __init__(self, database_url: str):
        self.database_url = database_url

        self.is_async = database_url.startswith("postgresql+asyncpg") or database_url.startswith("sqlite+aiosqlite")

        if self.is_async:
            self.engine = create_async_engine(database_url, echo=False, future=True)
            self.SessionFactory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        else:
            connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
            self.engine = create_engine(
                database_url,
                connect_args=connect_args,
                echo=False
            )
            self.SessionFactory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

    async def create_tables(self):
        """Create all tables"""
        from src.infrastructure.database.models import Base

        if self.is_async:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            Base.metadata.create_all(bind=self.engine)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        """Get a database session"""
        if self.is_async:
            async with self.SessionFactory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        else:
            session = self.SessionFactory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()


_db_connection: DatabaseConnection | None = None


def initialize_database(database_url: str = None) -> DatabaseConnection:
    """Initialize database connection"""
    global _db_connection

    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./credits.db")

    _db_connection = DatabaseConnection(database_url)
    return _db_connection


def get_database() -> DatabaseConnection:
    """Get the database connection instance"""
    global _db_connection
    if _db_connection is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _db_connection

```

`image_backend/src/infrastructure/database/models.py`:

```py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    """SQLAlchemy User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, index=True, nullable=False)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    credits = Column(Integer, default=0, nullable=False)
    total_purchased = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class TransactionModel(Base):
    """SQLAlchemy Transaction model"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    stripe_payment_id = Column(String(255), unique=True, nullable=True)
    type = Column(String(50), nullable=False)
    credits = Column(Integer, nullable=False)
    amount = Column(Float, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

```

`image_backend/src/infrastructure/external_services/__init__.py`:

```py
from src.infrastructure.external_services.gemini_image_generator import GeminiImageGenerator
from src.infrastructure.external_services.stripe_payment_gateway import StripePaymentGateway

__all__ = ["GeminiImageGenerator", "StripePaymentGateway"]

```

`image_backend/src/infrastructure/external_services/gemini_image_generator.py`:

```py
import base64

from google import genai
from google.genai import types

from src.domain.services.image_generator import GenerationRequest, ImageGenerator


class GeminiImageGenerator(ImageGenerator):
    """Gemini API implementation of ImageGenerator"""

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-2.5-flash-image"

    async def generate(self, request: GenerationRequest) -> list[str]:
        """Generate images using Gemini API"""
        generated_images = []
        variations = self._create_prompt_variations(request.prompt, request.variations)

        for i, variant_prompt in enumerate(variations):
            try:
                print(f"Generating variation {i + 1}/{request.variations}...")

                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        response = self._client.models.generate_content(
                            model=self._model,
                            contents=[variant_prompt, request.reference_image],
                            config=types.GenerateContentConfig(
                                response_modalities=["IMAGE"],
                                image_config=types.ImageConfig(aspect_ratio="1:1")
                            ),
                        )

                        if response and response.candidates:
                            candidate = response.candidates[0]
                            if candidate.content and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if getattr(part, "inline_data", None):
                                        mime = getattr(part.inline_data, "mime_type", "image/png")
                                        encoded = base64.b64encode(part.inline_data.data).decode("utf-8")
                                        generated_images.append(f"data:{mime};base64,{encoded}")
                                        break
                                break

                    except Exception as retry_error:
                        print(f"Attempt {attempt + 1} failed: {retry_error}")
                        if attempt == max_retries - 1:
                            raise

            except Exception as e:
                print(f"Error generating variation {i + 1}: {e!s}")
                continue

        if not generated_images:
            raise Exception("Failed to generate any images after all attempts")

        return generated_images

    def _create_prompt_variations(self, base_prompt: str, count: int) -> list[str]:
        """Create variations of the base prompt"""
        variations = [
            f"{base_prompt} High-resolution, photorealistic quality with natural daylight.",
            f"{base_prompt} Professional studio lighting with soft shadows and realistic details.",
            f"{base_prompt} Natural outdoor lighting with authentic textures and lifelike appearance."
        ]
        return variations[:count]

```

`image_backend/src/infrastructure/external_services/stripe_payment_gateway.py`:

```py
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

```

`image_backend/src/infrastructure/repositories/__init__.py`:

```py
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

__all__ = ["SQLAlchemyTransactionRepository", "SQLAlchemyUserRepository"]

```

`image_backend/src/infrastructure/repositories/transaction_repository.py`:

```py

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities.credit_transaction import CreditTransaction, TransactionType
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.money import Money
from src.infrastructure.database.models import TransactionModel


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository"""

    def __init__(self, session: Session):
        self._session = session

    async def save(self, transaction: CreditTransaction) -> CreditTransaction:
        """Save a new transaction"""
        model = self._to_model(transaction)
        self._session.add(model)

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def find_by_user_id(self, user_id: int, limit: int = 50) -> list[CreditTransaction]:
        """Find transactions for a user"""
        if hasattr(self._session, "execute"):  # Async session
            result = self._session.execute(
                select(TransactionModel)
                .where(TransactionModel.user_id == user_id)
                .order_by(TransactionModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
        else:  # Sync session
            models = (
                self._session.query(TransactionModel)
                .filter(TransactionModel.user_id == user_id)
                .order_by(TransactionModel.created_at.desc())
                .limit(limit)
                .all()
            )

        return [self._to_entity(model) for model in models]

    async def find_by_payment_id(self, payment_id: str) -> CreditTransaction | None:
        """Find transaction by payment ID"""
        if hasattr(self._session, "execute"):  # Async session
            result = self._session.execute(
                select(TransactionModel).where(TransactionModel.stripe_payment_id == payment_id)
            )
            model = result.scalar_one_or_none()
        else:  # Sync session
            model = (
                self._session.query(TransactionModel)
                .filter(TransactionModel.stripe_payment_id == payment_id)
                .first()
            )

        return self._to_entity(model) if model else None

    def _to_entity(self, model: TransactionModel) -> CreditTransaction:
        """Convert ORM model to domain entity"""
        return CreditTransaction(
            id=model.id,
            user_id=model.user_id,
            transaction_type=TransactionType(model.type),
            credits=Credits(model.credits),
            amount=Money(model.amount) if model.amount else None,
            payment_id=model.stripe_payment_id,
            description=model.description,
            created_at=model.created_at
        )

    def _to_model(self, entity: CreditTransaction) -> TransactionModel:
        """Convert domain entity to ORM model"""
        return TransactionModel(
            id=entity.id,
            user_id=entity.user_id,
            stripe_payment_id=entity.payment_id,
            type=entity.transaction_type.value,
            credits=entity.credits.value,
            amount=entity.amount.value if entity.amount else None,
            description=entity.description,
            created_at=entity.created_at
        )

```

`image_backend/src/infrastructure/repositories/user_repository.py`:

```py

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.credits import Credits
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: Session):
        self._session = session

    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
        else:
            model = self._session.query(UserModel).filter(UserModel.id == user_id).first()

        return self._to_entity(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(select(UserModel).where(UserModel.email == email.value))
            model = result.scalar_one_or_none()
        else:
            model = self._session.query(UserModel).filter(UserModel.email == email.value).first()

        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        """Save a new user"""
        model = self._to_model(user)
        self._session.add(model)

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def update(self, user: User) -> User:
        """Update an existing user"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            model = result.scalar_one()
        else:
            model = self._session.query(UserModel).filter(UserModel.id == user.id).one()

        model.email = user.email.value
        model.credits = user.credits.value
        model.stripe_customer_id = user.stripe_customer_id
        model.total_purchased = user.total_purchased.value
        model.updated_at = user.updated_at

        if hasattr(self._session, "flush"):
            self._session.flush()
        else:
            self._session.flush()

        return self._to_entity(model)

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        if hasattr(self._session, "execute"):
            result = self._session.execute(
                select(UserModel.id).where(UserModel.email == email.value)
            )
            return result.scalar_one_or_none() is not None
        return self._session.query(UserModel.id).filter(UserModel.email == email.value).first() is not None

    def _to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity"""
        return User(
            id=model.id,
            email=Email(model.email),
            credits=Credits(model.credits),
            stripe_customer_id=model.stripe_customer_id,
            total_purchased=Money(model.total_purchased),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to ORM model"""
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            credits=entity.credits.value,
            stripe_customer_id=entity.stripe_customer_id,
            total_purchased=entity.total_purchased.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

```

`image_backend/src/main.py`:

```py
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.connection import initialize_database
from src.presentation.api.routes import credits, feedback, health, image_generation, payments, webhooks
from src.infrastructure.config.settings import get_settings, initialize_settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting AI Photo Generation Service...")

    # Initialize settings
    settings = initialize_settings()
    print(f"Environment: {settings.environment}")

    # Initialize database
    db = initialize_database(settings.database_url)
    await db.create_tables()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")


def create_application() -> FastAPI:
    """Factory function to create FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="AI Photo Generation API",
        description="Clean Architecture implementation for AI-powered image generation with credit system",
        version="2.0.0",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router)
    app.include_router(feedback.router)
    app.include_router(credits.router)
    app.include_router(payments.router)
    app.include_router(webhooks.router)
    app.include_router(image_generation.router)

    return app


app = create_application()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        timeout_keep_alive=600,
        timeout_graceful_shutdown=30
    )
```

`image_backend/src/presentation/api/dependencies.py`:

```py
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.use_cases.complete_payment import CompletePaymentUseCase
from src.application.use_cases.generate_image import GenerateImageUseCase
from src.application.use_cases.get_user_credits import GetUserCreditsUseCase
from src.application.use_cases.purchase_credits import PurchaseCreditsUseCase
from src.application.use_cases.submit_feedback import SubmitFeedbackUseCase
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.database.connection import get_database
from src.infrastructure.external_services.gemini_image_generator import GeminiImageGenerator
from src.infrastructure.external_services.stripe_payment_gateway import StripePaymentGateway
from src.infrastructure.repositories import SQLAlchemyTransactionRepository, SQLAlchemyUserRepository


async def get_db_session() -> AsyncGenerator[Session, None]:
    """Get database session"""
    db = get_database()
    async with db.get_session() as session:
        yield session


def get_app_settings() -> Settings:
    """Get application settings"""
    return get_settings()


def get_user_repository(session: Session = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    """Get user repository"""
    return SQLAlchemyUserRepository(session)


def get_transaction_repository(session: Session = Depends(get_db_session)) -> SQLAlchemyTransactionRepository:
    """Get transaction repository"""
    return SQLAlchemyTransactionRepository(session)


def get_image_generator(settings: Settings = Depends(get_app_settings)) -> GeminiImageGenerator:
    """Get image generator service"""
    return GeminiImageGenerator(api_key=settings.gemini_api_key)


def get_payment_gateway(settings: Settings = Depends(get_app_settings)) -> StripePaymentGateway:
    """Get payment gateway service"""
    return StripePaymentGateway(
        api_key=settings.stripe_secret_key,
        webhook_secret=settings.stripe_webhook_secret
    )


def get_generate_image_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    image_generator: GeminiImageGenerator = Depends(get_image_generator)
) -> GenerateImageUseCase:
    """Get generate image use case"""
    return GenerateImageUseCase(user_repo, transaction_repo, image_generator)


def get_purchase_credits_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    payment_gateway: StripePaymentGateway = Depends(get_payment_gateway)
) -> PurchaseCreditsUseCase:
    """Get purchase credits use case"""
    return PurchaseCreditsUseCase(user_repo, payment_gateway)


def get_complete_payment_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository)
) -> CompletePaymentUseCase:
    """Get complete payment use case"""
    return CompletePaymentUseCase(user_repo, transaction_repo)


def get_user_credits_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetUserCreditsUseCase:
    """Get user credits use case"""
    return GetUserCreditsUseCase(user_repo)


def get_submit_feedback_use_case() -> SubmitFeedbackUseCase:
    """Get submit feedback use case"""
    return SubmitFeedbackUseCase()

```

`image_backend/src/presentation/api/error_handlers.py`:

```py
from fastapi import HTTPException, status

from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainException,
    ImageGenerationError,
    InsufficientCreditsError,
    InvalidCreditPackageError,
    InvalidEmailError,
    PaymentProcessingError,
    UserNotFoundError,
)


def map_domain_exception_to_http(exception: Exception) -> HTTPException:
    """Map domain exceptions to HTTP exceptions"""
    if isinstance(exception, InsufficientCreditsError):
        return HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exception)
        )

    if isinstance(exception, UserNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception)
        )

    if isinstance(exception, InvalidEmailError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    if isinstance(exception, InvalidCreditPackageError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    if isinstance(exception, ImageGenerationError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {exception!s}"
        )

    if isinstance(exception, PaymentProcessingError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {exception!s}"
        )

    if isinstance(exception, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exception)
        )

    if isinstance(exception, AuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exception)
        )

    if isinstance(exception, DomainException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

    # Generic exception
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )

```

`image_backend/src/presentation/api/routes/__init__.py`:

```py
__all__ = ["credits", "feedback", "health", "image_generation", "payments", "webhooks"]

```

`image_backend/src/presentation/api/routes/credits.py`:

```py
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

```

`image_backend/src/presentation/api/routes/feedback.py`:

```py
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

```

`image_backend/src/presentation/api/routes/health.py`:

```py
from fastapi import APIRouter

from src.presentation.api.schemas.responses import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="AI Photo Generation"
    )

```

`image_backend/src/presentation/api/routes/image_generation.py`:

```py
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image

from src.application.use_cases.generate_image import GenerateImageRequest, GenerateImageUseCase
from src.presentation.api.dependencies import get_generate_image_use_case
from src.presentation.api.error_handlers import map_domain_exception_to_http
from src.presentation.api.schemas.responses import ImageGenerationResponse

router = APIRouter(prefix="/api", tags=["generation"])


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
        prompt: str = Form(...),
        image: UploadFile = File(...),
        transformation_mode: str = Form(default="full-transformation"),
        user_email: str = Form(...),
        use_case: GenerateImageUseCase = Depends(get_generate_image_use_case)
):
    """Generate AI images based on prompt and reference image"""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image."
        )

    try:
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))
        request = GenerateImageRequest(
            email=user_email,
            prompt=prompt,
            image=pil_image,
            transformation_mode=transformation_mode
        )
        result = await use_case.execute(request)

        if result.is_failure():
            raise map_domain_exception_to_http(result.error)

        return ImageGenerationResponse(
            images=result.value.images,
            credits_remaining=result.value.credits_remaining
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in image generation endpoint: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))

```

`image_backend/src/presentation/api/routes/payments.py`:

```py
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

```

`image_backend/src/presentation/api/routes/webhooks.py`:

```py
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

```

`image_backend/src/presentation/api/schemas/__init__.py`:

```py
from src.presentation.api.schemas.requests import CheckoutRequest, FeedbackRequest, GenerateImageFormRequest
from src.presentation.api.schemas.responses import (
    CheckoutResponse,
    CreditsResponse,
    ErrorResponse,
    FeedbackResponse,
    HealthResponse,
    ImageGenerationResponse,
    WebhookResponse,
)

__all__ = [
    "CheckoutRequest",
    "CheckoutResponse",
    "CreditsResponse",
    "ErrorResponse",
    "FeedbackRequest",
    "FeedbackResponse",
    "GenerateImageFormRequest",
    "HealthResponse",
    "ImageGenerationResponse",
    "WebhookResponse",
]

```

`image_backend/src/presentation/api/schemas/requests.py`:

```py

from pydantic import BaseModel, EmailStr, Field


class FeedbackRequest(BaseModel):
    """Request schema for feedback submission"""

    message: str = Field(..., min_length=1, max_length=5000)
    email: EmailStr | None = None


class CheckoutRequest(BaseModel):
    """Request schema for creating checkout session"""

    email: EmailStr
    package: str = Field(..., pattern="^(starter|pro|business)$")


class GenerateImageFormRequest(BaseModel):
    """Form request for image generation"""

    prompt: str = Field(..., min_length=1)
    transformation_mode: str = Field(default="full-transformation")
    user_email: EmailStr

```

`image_backend/src/presentation/api/schemas/responses.py`:

```py

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str
    error_code: str | None = None


class FeedbackResponse(BaseModel):
    """Response schema for feedback"""

    ok: bool


class CreditsResponse(BaseModel):
    """Response schema for user credits"""

    credits: int
    email: str


class CheckoutResponse(BaseModel):
    """Response schema for checkout session"""

    checkout_url: str
    session_id: str


class ImageGenerationResponse(BaseModel):
    """Response schema for image generation"""

    images: list[str]
    credits_remaining: int


class HealthResponse(BaseModel):
    """Response schema for health check"""

    status: str
    service: str


class WebhookResponse(BaseModel):
    """Response schema for webhooks"""

    status: str

```

`image_backend/src/shared/result.py`:

```py
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T]):
    """Base result class"""

    def is_success(self) -> bool:
        return isinstance(self, Success)

    def is_failure(self) -> bool:
        return isinstance(self, Failure)

    @property
    def value(self) -> T:
        if isinstance(self, Success):
            return self._value
        raise ValueError("Cannot get value from Failure")

    @property
    def error(self) -> Exception:
        if isinstance(self, Failure):
            return self._error
        raise ValueError("Cannot get error from Success")


class Success(Result[T]):
    """Represents a successful result"""

    def __init__(self, value: T):
        self._value = value

    def __repr__(self) -> str:
        return f"Success({self._value})"


class Failure(Result[T]):
    """Represents a failed result"""

    def __init__(self, error: Exception):
        self._error = error

    def __repr__(self) -> str:
        return f"Failure({self._error})"

```
