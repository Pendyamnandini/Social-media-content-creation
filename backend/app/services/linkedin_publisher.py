import os
import requests
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.linkedin import LinkedInConnection, ConnectionStatus, GeneratedPost, PostStatus, PublishingRecord
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LinkedInPublisher:
    def __init__(self):
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID")
        self.client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("LINKEDIN_REDIRECT_URI", "http://localhost:5173/dashboard/linkedin-agent/callback")
        self.api_version = os.environ.get("LINKEDIN_API_VERSION", "202608")
        
    def get_auth_url(self, state: str) -> str:
        url = (
            "https://www.linkedin.com/oauth/v2/authorization?"
            "response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
            "&scope=openid%20profile%20w_member_social"
        )
        return url

    def exchange_code(self, code: str, user_id: int, db: Session):
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to exchange token: {response.text}")
            raise Exception("Failed to connect LinkedIn")
            
        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 5184000) # Default 60 days
        
        # Get user profile
        profile_response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if profile_response.status_code != 200:
            logger.error(f"Failed to get profile: {profile_response.text}")
            raise Exception("Failed to fetch LinkedIn profile")
            
        profile_data = profile_response.json()
        member_id = profile_data.get("sub")
        name = profile_data.get("name")
        picture = profile_data.get("picture")
        
        # Save to DB
        connection = db.query(LinkedInConnection).filter(LinkedInConnection.user_id == user_id).first()
        if not connection:
            connection = LinkedInConnection(user_id=user_id)
            db.add(connection)
            
        connection.linkedin_member_id = member_id
        connection.linkedin_profile_name = name
        connection.linkedin_profile_picture = picture
        connection.access_token_encrypted = access_token # In a real app, encrypt this
        connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        connection.status = ConnectionStatus.CONNECTED
        connection.scopes = "openid profile w_member_social"
        
        db.commit()
        return connection

    def publish_post(self, post_id: int, user_id: int, db: Session):
        post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id, GeneratedPost.user_id == user_id).first()
        if not post or post.status == PostStatus.PUBLISHED:
            raise Exception("Post not found or already published")
            
        connection = db.query(LinkedInConnection).filter(LinkedInConnection.user_id == user_id).first()
        if not connection or connection.status != ConnectionStatus.CONNECTED:
            raise Exception("LinkedIn not connected")
            
        # Combine post and hashtags
        hashtags_list = []
        if post.hashtags:
            try:
                # Try to load as JSON array
                parsed = json.loads(post.hashtags)
                if isinstance(parsed, list):
                    hashtags_list = parsed
                else:
                    hashtags_list = [str(parsed)]
            except json.JSONDecodeError:
                # If it's a plain string, just use it directly
                hashtags_list = [post.hashtags]
                
        full_text = post.post_content
        if hashtags_list:
            full_text += "\n\n" + " ".join(hashtags_list)
            
        url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {connection.access_token_encrypted}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": self.api_version,
            "Content-Type": "application/json"
        }
        
        # Ensure correct urn format
        person_urn = f"urn:li:person:{connection.linkedin_member_id}"
        
        # If there's an image, we need to upload it first
        image_urn = None
        if post.image_url:
            try:
                import io
                import base64
                from PIL import Image
                
                # 1. Retrieve image binary
                img_data = None
                if post.image_url.startswith("data:image"):
                    header, encoded = post.image_url.split(",", 1)
                    img_data = base64.b64decode(encoded)
                elif post.image_url.startswith("http"):
                    img_resp = requests.get(post.image_url)
                    if img_resp.status_code != 200:
                        raise Exception(f"Failed to download generated image: HTTP {img_resp.status_code}")
                    img_data = img_resp.content
                else:
                    with open(post.image_url, "rb") as f:
                        img_data = f.read()
                        
                if not img_data:
                    raise Exception("Image data is empty.")
                    
                # Validate and convert to JPEG
                try:
                    img = Image.open(io.BytesIO(img_data))
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=95)
                    processed_img_data = output.getvalue()
                except Exception as e:
                    raise Exception(f"Invalid image format or corrupted image: {e}")
                    
                # 2. Initialize upload
                logger.info("LinkedIn image upload registration started")
                init_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
                init_data = {
                    "initializeUploadRequest": {
                        "owner": person_urn
                    }
                }
                init_resp = requests.post(init_url, headers=headers, json=init_data)
                if init_resp.status_code == 200:
                    init_result = init_resp.json().get("value", {})
                    upload_url = init_result.get("uploadUrl")
                    image_urn = init_result.get("image")
                    
                    # 3. Upload image binary
                    if upload_url and image_urn:
                        logger.info(f"LinkedIn image upload started for URN: {image_urn}")
                        put_headers = {
                            "Authorization": f"Bearer {connection.access_token_encrypted}",
                            "Content-Type": "image/jpeg"
                        }
                        put_resp = requests.put(upload_url, headers=put_headers, data=processed_img_data)
                        if put_resp.status_code != 201:
                            error_msg = f"Failed to upload image binary to LinkedIn: {put_resp.text}"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                        logger.info("LinkedIn image upload successful")
                        logger.info(f"LinkedIn media URN obtained: {image_urn}")
                        
                        # 4. Poll image status
                        import time
                        import urllib.parse
                        encoded_urn = urllib.parse.quote(image_urn)
                        status_url = f"https://api.linkedin.com/rest/images/{encoded_urn}"
                        
                        max_retries = 10
                        poll_interval = 2
                        image_ready = False
                        
                        for _ in range(max_retries):
                            status_resp = requests.get(status_url, headers=headers)
                            if status_resp.status_code == 200:
                                status_data = status_resp.json()
                                current_status = status_data.get("status")
                                if current_status == "AVAILABLE":
                                    image_ready = True
                                    break
                                elif current_status == "PROCESSING_FAILED":
                                    raise Exception(f"LinkedIn failed to process the image: {status_data}")
                            time.sleep(poll_interval)
                            
                        if not image_ready:
                            raise Exception("Image processing timed out on LinkedIn. Please try again.")
                    else:
                        error_msg = f"Failed to get uploadUrl or image URN from LinkedIn: {init_resp.text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                else:
                    error_msg = f"Failed to initialize image upload with LinkedIn: {init_resp.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                logger.error(f"Error uploading image to LinkedIn: {str(e)}")
                raise Exception(f"Image upload failed. The text-only post was not published. Error: {str(e)}")

        data = {
            "author": person_urn,
            "commentary": full_text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        if image_urn:
            data["content"] = {
                "media": {
                    "id": image_urn,
                    "title": "Generated LinkedIn Image",
                    "altText": "AI generated image for LinkedIn post"
                }
            }
        
        # Create publishing record
        record = PublishingRecord(
            user_id=user_id,
            generated_post_id=post.id,
            status=PostStatus.PUBLISHING
        )
        db.add(record)
        post.status = PostStatus.PUBLISHING
        db.commit()
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                # Success
                post.status = PostStatus.PUBLISHED
                record.status = PostStatus.PUBLISHED
                platform_post_id = response.headers.get("x-restli-id", "")
                record.platform_post_id = platform_post_id
                record.published_at = datetime.utcnow()
                db.commit()
                return {
                    "success": True,
                    "message": "LinkedIn post published successfully with image and text." if image_urn else "LinkedIn post published successfully.",
                    "postId": platform_post_id,
                    "mediaAttached": bool(image_urn),
                    "mediaUrn": image_urn if image_urn else None
                }
            else:
                logger.error(f"LinkedIn publishing failed: {response.text}")
                post.status = PostStatus.FAILED
                record.status = PostStatus.FAILED
                record.error_message = response.text
                db.commit()
                raise Exception(f"Failed to create LinkedIn post: {response.text}")
        except Exception as e:
            post.status = PostStatus.FAILED
            record.status = PostStatus.FAILED
            record.error_message = str(e)
            db.commit()
            raise Exception(str(e))

linkedin_publisher = LinkedInPublisher()
