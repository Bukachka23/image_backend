
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
