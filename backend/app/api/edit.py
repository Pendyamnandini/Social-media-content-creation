from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
import logging
from app.ai.orchestrator import orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/edit")
async def process_image_edit(
    instructions: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Pass through the new Advanced Orchestrator Pipeline
        edited_image_bytes = orchestrator.process_request(image_bytes, instructions)
        
        # Return image directly
        return Response(content=edited_image_bytes, media_type="image/jpeg")
        
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
