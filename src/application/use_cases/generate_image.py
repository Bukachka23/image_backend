
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
