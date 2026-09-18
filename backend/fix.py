import os
import re

# Update linkedin.py
with open('d:/socialpilot-ai/backend/app/api/linkedin.py', 'r') as f:
    content = f.read()

if '/posts/{post_id}/refresh_image' not in content:
    with open('d:/socialpilot-ai/backend/app/api/linkedin.py', 'a') as f:
        f.write('''
@router.post("/posts/{post_id}/refresh_image")
def refresh_image(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id, GeneratedPost.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    try:
        new_image_url = linkedin_ai_service.regenerate_image(post.content_analysis)
        post.image_url = new_image_url
        db.commit()
        return {"success": True, "image_url": new_image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''')
