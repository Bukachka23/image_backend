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
