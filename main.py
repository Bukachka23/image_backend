from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel, EmailStr
import base64

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=gemini_api_key)

class ImageGenerationResponse(BaseModel):
    images: list[str]

# --- Update 5: Feedback model + endpoint ---
class FeedbackPayload(BaseModel):
    message: str
    email: EmailStr | None = None

@app.post("/api/feedback")
async def feedback_endpoint(payload: FeedbackPayload):
    msg = (payload.message or '').strip()
    if not msg:
      raise HTTPException(status_code=400, detail="Empty feedback.")
    # Minimal handling: log to stdout; integrate DB or email later.
    print(f"[FEEDBACK] from={payload.email or 'anonymous'} :: {msg[:500]}")
    return {"ok": True}

@app.post("/api/generate", response_model=ImageGenerationResponse)
async def generate_image_endpoint(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    transformation_mode: str = Form(default="full-transformation")
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))

        # Use transformation_mode to determine the prompt strategy
        if transformation_mode == "item-only" or "Same person, same pose, same composition" in prompt:
            # Item-only transformation mode
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
            # Full transformation mode
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
                print(f"Generating variation {i+1}/3...")

                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[variant_prompt, pil_image],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio="1:1")
                    ),
                )

                if not response or not response.candidates:
                    print(f"No candidates in response for variation {i+1}")
                    continue

                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                    safety_ratings = getattr(candidate, 'safety_ratings', [])
                    print(f"Variation {i+1} failed. Finish reason: {finish_reason}, Safety: {safety_ratings}")
                    continue

                parts = candidate.content.parts
                for part in parts:
                    if getattr(part, "inline_data", None):
                        mime = getattr(part.inline_data, "mime_type", "image/png")
                        encoded = base64.b64encode(part.inline_data.data).decode("utf-8")
                        generated_images.append(f"data:{mime};base64,{encoded}")
                        break

            except Exception as e:
                print(f"Error generating variation {i+1}: {str(e)}")
                continue

        if not generated_images:
            raise HTTPException(
                status_code=500,
                detail="The AI model could not generate any images. This may be due to safety filters or content restrictions. Please try a different prompt."
            )

        print(f"Successfully generated {len(generated_images)} image variations")
        return ImageGenerationResponse(images=generated_images)

    except Exception as e:
        print(f"Error in image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
