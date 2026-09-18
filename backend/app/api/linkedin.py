from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.models.linkedin import LinkedInConnection, GeneratedPost, ConnectionStatus, PostStatus
from app.services.linkedin_ai_service import linkedin_ai_service
from app.services.linkedin_publisher import linkedin_publisher
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    image_description: Optional[str] = ""
    content_type: str = "Auto Detect"
    tone: str = "Professional"
    audience: str = "General LinkedIn Audience"
    length: str = "Medium"

class UpdatePostRequest(BaseModel):
    post_content: str
    hashtags: str
    suggested_comment: str
    suggested_message: str
    image_url: Optional[str] = None

@router.get("/status")
def get_linkedin_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    connection = db.query(LinkedInConnection).filter(LinkedInConnection.user_id == current_user.id).first()
    if not connection or connection.status != ConnectionStatus.CONNECTED:
        return {"connected": False}
    
    return {
        "connected": True,
        "profile_name": connection.linkedin_profile_name,
        "profile_picture": connection.linkedin_profile_picture,
        "profile_url": connection.profile_url,
        "is_manual": connection.access_token_encrypted is None
    }

@router.get("/connect")
def connect_linkedin(state: str, current_user: User = Depends(get_current_user)):
    if not linkedin_publisher.client_id or not linkedin_publisher.client_secret:
        raise HTTPException(status_code=400, detail="LinkedIn Developer App credentials (CLIENT_ID / SECRET) are not configured in backend/.env")
    url = linkedin_publisher.get_auth_url(state)
    return {"url": url}

class ManualConnectRequest(BaseModel):
    profile_url: str

@router.post("/connect_manual")
def connect_manual(req: ManualConnectRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    connection = db.query(LinkedInConnection).filter(LinkedInConnection.user_id == current_user.id).first()
    if not connection:
        connection = LinkedInConnection(user_id=current_user.id)
        db.add(connection)
        
    connection.profile_url = req.profile_url
    connection.status = ConnectionStatus.CONNECTED
    connection.linkedin_profile_name = "Manual User"
    connection.access_token_encrypted = None
    
    db.commit()
    return {"success": True}

@router.post("/callback")
def linkedin_callback(code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        linkedin_publisher.exchange_code(code, current_user.id, db)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/disconnect")
def disconnect_linkedin(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    connection = db.query(LinkedInConnection).filter(LinkedInConnection.user_id == current_user.id).first()
    if connection:
        connection.status = ConnectionStatus.DISCONNECTED
        db.commit()
    return {"success": True}

@router.post("/generate")
def generate_post(req: GenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = linkedin_ai_service.generate_content(
            prompt=req.prompt,
            image_description=req.image_description,
            content_type=req.content_type,
            tone=req.tone,
            audience=req.audience,
            length=req.length
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    post = GeneratedPost(
        user_id=current_user.id,
        original_prompt=req.prompt,
        post_content=data.get("post", ""),
        hashtags=json.dumps(data.get("hashtags", [])),
        suggested_comment=data.get("suggestedComment", ""),
        suggested_message=data.get("suggestedMessage", ""),
        image_url=data.get("imageUrl", ""),
        content_type=data.get("contentType", ""),
        tone=data.get("tone", ""),
        audience=data.get("audience", ""),
        content_analysis=json.dumps(data.get("analysis", {})),
        image_prompt=data.get("imagePrompt", ""),
        status=PostStatus.DRAFT
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "post_content": post.post_content,
        "hashtags": json.loads(post.hashtags) if post.hashtags else [],
        "suggested_comment": post.suggested_comment,
        "suggested_message": post.suggested_message,
        "image_url": post.image_url,
        "status": post.status,
        "requested_mentions": data.get("requested_mentions", []),
        "content_analysis": json.loads(post.content_analysis) if post.content_analysis else {}
    }

@router.post("/posts/{post_id}/approve")
def approve_post(post_id: int, req: UpdatePostRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id, GeneratedPost.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    post.post_content = req.post_content
    post.hashtags = req.hashtags
    post.suggested_comment = req.suggested_comment
    post.suggested_message = req.suggested_message
    if req.image_url is not None:
        post.image_url = req.image_url
    post.status = PostStatus.APPROVED
    db.commit()
    return {"success": True}

@router.post("/posts/{post_id}/publish")
def publish_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = linkedin_publisher.publish_post(post_id, current_user.id, db)
        return result
    except Exception as e:
        error_message = str(e)
        stage = "IMAGE_UPLOAD" if "image" in error_message.lower() else "POST_CREATION"
        return {
            "success": False, 
            "message": error_message, 
            "stage": stage,
            "textOnlyPublished": False,
            "mediaAttached": False
        }

@router.post("/posts/{post_id}/refresh_image")
def refresh_image(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id, GeneratedPost.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    try:
        new_image_url = linkedin_ai_service.regenerate_image(post.content_analysis, post.image_prompt)
        post.image_url = new_image_url
        db.commit()
        return {"success": True, "image_url": new_image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
