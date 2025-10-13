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
