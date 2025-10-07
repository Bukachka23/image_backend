from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel
import base64

load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
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
                f"Keep the exact same person, pose, and photo composition. "
                f"Only change the clothing/outfit to '{style}' style. "
                f"Maintain facial features, body position, and background exactly as they are."
            )
            print(f"Using item-only mode for style: {style}")
        else:
            # Full transformation mode
            style = prompt.partition("style of")[2].strip().strip(".")
            generation_prompt = (
                f"Create a new photo of this person in a '{style}' theme. "
                f"Transform the entire scene with new background, pose, and outfit "
                f"that reflects '{style}' naturally. Create an artistic interpretation."
            )
            print(f"Using full transformation mode for style: {style}")

        # Generate 3 variations
        generated_images = []
        variations = [
            f"{generation_prompt} Style variation 1.",
            f"{generation_prompt} Style variation 2 with different lighting.",
            f"{generation_prompt} Style variation 3 with unique artistic interpretation."
        ]
        
        for i, variant_prompt in enumerate(variations):
            try:
                print(f"Generating variation {i+1}/3...")
                
                # ✅ Use image-capable model + ask for IMAGE output
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[variant_prompt, pil_image],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio="1:1")
                    ),
                )

                # Check if response has valid candidates
                if not response or not response.candidates:
                    print(f"No candidates in response for variation {i+1}")
                    continue
                
                # Check if the first candidate has content
                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    # Check for safety ratings or finish reason
                    finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                    safety_ratings = getattr(candidate, 'safety_ratings', [])
                    
                    error_msg = f"Variation {i+1} failed. Finish reason: {finish_reason}"
                    if safety_ratings:
                        error_msg += f", Safety ratings: {safety_ratings}"
                    
                    print(error_msg)
                    continue
                
                # Extract the image from the response
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
        
        # Check if we generated at least one image
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
