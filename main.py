from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel, EmailStr
import base64
import stripe
from sqlalchemy.orm import Session
from database import get_db, User, Transaction
from datetime import datetime

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable not set.")

client = genai.Client(api_key=gemini_api_key)

# Credit packages
CREDIT_PACKAGES = {
    "starter": {"credits": 10, "price": 9.99, "name": "Starter Pack"},
    "pro": {"credits": 50, "price": 39.99, "name": "Pro Pack"},
    "business": {"credits": 150, "price": 99.99, "name": "Business Pack"},
}

CREDITS_PER_GENERATION = 3  # Each generation costs 3 credits


# Models
class ImageGenerationResponse(BaseModel):
    images: list[str]
    credits_remaining: int


class FeedbackPayload(BaseModel):
    message: str
    email: EmailStr | None = None


class CheckoutRequest(BaseModel):
    email: EmailStr
    package: str


class CreditsResponse(BaseModel):
    credits: int
    email: str


# Helper functions
def get_or_create_user(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, credits=0)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def deduct_credits(db: Session, user: User, credits: int, description: str):
    if user.credits < credits:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    user.credits -= credits
    user.updated_at = datetime.now()

    transaction = Transaction(
        user_id=user.id,
        type="usage",
        credits=-credits,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(user)


def add_credits(db: Session, user: User, credits: int, amount: float, payment_id: str, description: str):
    user.credits += credits
    user.total_purchased += amount
    user.updated_at = datetime.now()

    transaction = Transaction(
        user_id=user.id,
        stripe_payment_id=payment_id,
        type="purchase",
        credits=credits,
        amount=amount,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(user)


# Endpoints
@app.post("/api/feedback")
async def feedback_endpoint(payload: FeedbackPayload):
    msg = (payload.message or '').strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Empty feedback.")
    print(f"[FEEDBACK] from={payload.email or 'anonymous'} :: {msg[:500]}")
    return {"ok": True}


@app.get("/api/credits/{email}")
async def get_credits(email: str, db: Session = Depends(get_db)):
    user = get_or_create_user(db, email)
    return CreditsResponse(credits=user.credits, email=user.email)


@app.post("/api/checkout")
async def create_checkout_session(request: CheckoutRequest, db: Session = Depends(get_db)):
    if request.package not in CREDIT_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    package = CREDIT_PACKAGES[request.package]
    user = get_or_create_user(db, str(request.email))

    # Create or retrieve Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=request.email)
        user.stripe_customer_id = customer.id
        db.commit()

    try:
        # Create Checkout Session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(package["price"] * 100),  # Convert to cents
                        "product_data": {
                            "name": package["name"],
                            "description": f"{package['credits']} credits for AI photo generation",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{frontend_url}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}?payment=cancelled",
            metadata={
                "user_email": request.email,
                "package": request.package,
                "credits": package["credits"],
            }
        )

        return {"checkout_url": session.url, "session_id": session.id}

    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe-webhook")
async def stripe_webhook(
        request: bytes = Depends(lambda: None),
        stripe_signature: str = Header(None, alias="stripe-signature"),
        db: Session = Depends(get_db)
):
    from fastapi import Request as FastAPIRequest

    # Get raw body
    async def get_raw_body(request: FastAPIRequest):
        return await request.body()

    if not stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    try:
        # This will be called properly by FastAPI with the raw request body
        from starlette.requests import Request

        # Create a proper dependency
        async def get_request_body(request: Request):
            return await request.body()

        event = None

        # For now, log the webhook call
        print("Webhook received")

        return {"status": "success"}

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Proper webhook endpoint
from starlette.requests import Request as StarletteRequest


@app.post("/api/webhooks/stripe")
async def stripe_webhook_handler(request: StarletteRequest, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not stripe_webhook_secret:
        print("Warning: STRIPE_WEBHOOK_SECRET not set")
        return JSONResponse({"status": "success"})

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Get metadata
        user_email = session["metadata"].get("user_email")
        package = session["metadata"].get("package")
        credits = int(session["metadata"].get("credits", 0))

        if user_email and package and credits:
            user = get_or_create_user(db, user_email)
            package_info = CREDIT_PACKAGES[package]

            add_credits(
                db, user, credits, package_info["price"],
                session["id"], f"Purchase: {package_info['name']}"
            )

            print(f"Credits added: {user_email} +{credits} credits")

    return JSONResponse({"status": "success"})


@app.post("/api/generate", response_model=ImageGenerationResponse)
async def generate_image_endpoint(
        prompt: str = Form(...),
        image: UploadFile = File(...),
        transformation_mode: str = Form(default="full-transformation"),
        user_email: str = Form(...),
        db: Session = Depends(get_db)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    # Check user credits
    user = get_or_create_user(db, user_email)
    if user.credits < CREDITS_PER_GENERATION:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. You need {CREDITS_PER_GENERATION} credits but have {user.credits}. Please purchase more credits."
        )

    # Deduct credits before generation
    deduct_credits(db, user, CREDITS_PER_GENERATION, "Image generation (3 variations)")

    try:
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))

        # Use transformation_mode to determine the prompt strategy
        if transformation_mode == "item-only" or "Same person, same pose, same composition" in prompt:
            if "only change to" in prompt:
                style = prompt.split("only change to")[1].strip().strip(".")
            else:
                style = prompt.partition("style of")[2].strip().strip(".")

            generation_prompt = (
                f"Create a highly realistic, photographic image. Keep the exact same person, pose, and photo composition. "
                f"Only change the clothing/outfit to '{style}' style. "
                f"Maintain facial features, body position, and background exactly as they are. "
                f"Use natural lighting, realistic skin texture, and professional photography quality. "
                f"Ensure the clothing looks authentic and properly fitted to the person's body."
            )
            print(f"Using item-only mode for style: {style}")
        else:
            style = prompt.partition("style of")[2].strip().strip(".")
            generation_prompt = (
                f"Create a highly realistic, professional photograph of this person in a '{style}' theme. "
                f"Transform the entire scene with an appropriate background, natural pose, and authentic outfit "
                f"that reflects '{style}' style. Use photographic quality with natural lighting, "
                f"realistic skin texture, proper shadows, and lifelike details. "
                f"Ensure the image looks like it was taken with a professional camera, not AI-generated."
            )
            print(f"Using full transformation mode for style: {style}")

        # Generate 3 variations
        generated_images = []
        variations = [
            f"{generation_prompt} High-resolution, photorealistic quality with natural daylight.",
            f"{generation_prompt} Professional studio lighting with soft shadows and realistic details.",
            f"{generation_prompt} Natural outdoor lighting with authentic textures and lifelike appearance."
        ]

        for i, variant_prompt in enumerate(variations):
            try:
                print(f"Generating variation {i + 1}/3...")

                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[variant_prompt, pil_image],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio="1:1")
                    ),
                )

                if not response or not response.candidates:
                    print(f"No candidates in response for variation {i + 1}")
                    continue

                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                    safety_ratings = getattr(candidate, 'safety_ratings', [])
                    print(f"Variation {i + 1} failed. Finish reason: {finish_reason}, Safety: {safety_ratings}")
                    continue

                parts = candidate.content.parts
                for part in parts:
                    if getattr(part, "inline_data", None):
                        mime = getattr(part.inline_data, "mime_type", "image/png")
                        encoded = base64.b64encode(part.inline_data.data).decode("utf-8")
                        generated_images.append(f"data:{mime};base64,{encoded}")
                        break

            except Exception as e:
                print(f"Error generating variation {i + 1}: {str(e)}")
                continue

        if not generated_images:
            # Refund credits if generation completely failed
            add_credits(db, user, CREDITS_PER_GENERATION, 0, "refund", "Generation failed - credits refunded")
            raise HTTPException(
                status_code=500,
                detail="The AI model could not generate any images. Your credits have been refunded."
            )

        print(f"Successfully generated {len(generated_images)} image variations")

        # Refresh user to get updated credits
        db.refresh(user)

        return ImageGenerationResponse(images=generated_images, credits_remaining=user.credits)

    except HTTPException:
        raise
    except Exception as e:
        # Refund credits on unexpected error
        add_credits(db, user, CREDITS_PER_GENERATION, 0, "refund", f"Error: {str(e)[:100]}")
        print(f"Error in image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Photo Generation"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)