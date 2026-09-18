from fastapi import APIRouter
from pydantic import BaseModel
import logging
from app.ai.text_generation import text_service

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateRequest(BaseModel):
    topic: str
    platform: str
    tone: str

@router.post("/generate")
def generate_content(req: GenerateRequest):
    try:
        return text_service.generate_content(req.topic, req.platform, req.tone)
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        # Final safety net returning a safe 500 equivalent message or a default dict
        return {
            "post_text": "An error occurred while generating content.",
            "visual_concept": "Error",
            "hashtags": [],
            "recommended_time": "N/A",
            "ai_suggestion": "Please check backend logs."
        }
