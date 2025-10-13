
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
