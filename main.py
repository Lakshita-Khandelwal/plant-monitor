import os
import base64
from typing import Annotated
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from anthropic import Anthropic
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Setup & Config
load_dotenv()

app = FastAPI(title="AI Plant Monitor Backend")

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL") or "", 
    os.getenv("SUPABASE_KEY") or ""
)
claude = Anthropic(api_key=os.getenv("CLAUDE_API_KEY") or "")

@app.post("/upload")
async def handle_plant_data(
    moisture: Annotated[str, Form(...)],
    light: Annotated[str, Form(...)],
    image: Annotated[UploadFile, File(...)]
):
    try:
        # 2. Process Image
        img_bytes = await image.read()
        # Claude needs base64 for the Vision API
        base64_img = base64.b64encode(img_bytes).decode("utf-8")
        
        # 3. Get AI Analysis from Claude 3.5 Sonnet
        # Using the latest model for improved botanical reasoning
        response = claude.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=500,
            system="You are a professional botanist. Analyze plant and accordingly give a health assessment from images and sensor data.",
            messages=[{
                "role": "user", 
                "content": [
                    {
                        "type": "image", 
                        "source": {
                            "type": "base64", 
                            "media_type": "image/jpeg", 
                            "data": base64_img
                        }
                    },
                    {
                        "type": "text", 
                        "text": f"The soil moisture sensor reads {moisture}% and the light sensor reads {light} lux. Based on the photo and sensor data, what is the health status and immediate next step?"
                    }
                ]
            }]
        )
        ai_advice = response.content[0].text

        # 4. Upload to Supabase Storage
        file_path = f"uploads/plant_{os.urandom(4).hex()}.jpg"
        # We specify the content type so the browser renders it instead of downloading
        supabase.storage.from_("plants").upload(
            path=file_path, 
            file=img_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        
        # 5. Get Public URL for the image
        img_url = supabase.storage.from_("plants").get_public_url(file_path)

        # 6. Insert into Database
        # This will trigger the "Realtime" update on your website automatically
        db_response = supabase.table("plant_logs").insert({
            "moisture": moisture,
            "light": light,
            "image_url": img_url,
            "claude_advice": ai_advice
        }).execute()

        return {
            "status": "success",
            "message": "Data logged and analyzed",
            "id": db_response.data[0]['id']
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "online"}

@app.get("/config")
def get_config():
    """Serve public Supabase configuration for frontend"""
    return {
        "supabaseUrl": os.getenv("SUPABASE_URL") or "",
        "supabaseAnonKey": os.getenv("SUPABASE_ANON_KEY") or ""
    }

@app.get("/")
def read_root():
    return FileResponse("static/index.html")