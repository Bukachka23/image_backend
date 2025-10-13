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
