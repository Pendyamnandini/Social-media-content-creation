import numpy as np
import cv2
import logging
import io
import os
import requests
from PIL import Image
from dotenv import load_dotenv

try:
    from rembg import remove
except ImportError:
    remove = None

load_dotenv()
logger = logging.getLogger(__name__)

# Path to our AI-generated high-quality blazer asset
BLAZER_ASSET_PATH = r"C:\Users\Nandi\.gemini\antigravity\brain\4a14cd2d-e3d9-4155-9779-7786d7f152e3\professional_blazer_1789117097421.jpg"

class GenerativeInpainter:
    def __init__(self):
        logger.info("Initializing Generative Inpainting Engine...")

    def overlay_blazer(self, user_img: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Dynamically aligns and overlays a high-quality AI-generated blazer onto the user.
        """
        if not os.path.exists(BLAZER_ASSET_PATH) or remove is None:
            return user_img # Fallback
            
        # 1. Process the blazer asset (Remove background)
        with open(BLAZER_ASSET_PATH, "rb") as f:
            blazer_bytes = f.read()
            
        blazer_no_bg = remove(blazer_bytes)
        nparr = np.frombuffer(blazer_no_bg, np.uint8)
        blazer_cv = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED) # Includes alpha channel
        
        # 2. Detect face in user image to align shoulders
        h, w = user_img.shape[:2]
        gray = cv2.cvtColor(user_img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            # Fallback alignment if no face detected
            face_bottom = int(h * 0.45)
            face_center = w // 2
        else:
            fx, fy, fw, fh = faces[0]
            face_bottom = fy + fh
            face_center = fx + fw // 2
            
        # 3. Resize and position the blazer
        # The blazer needs to cover from the chin/neck downwards
        blazer_h, blazer_w = blazer_cv.shape[:2]
        
        # Scale blazer so its width matches the user image width (or slightly larger)
        scale = (w * 1.5) / blazer_w
        new_w = int(blazer_w * scale)
        new_h = int(blazer_h * scale)
        blazer_resized = cv2.resize(blazer_cv, (new_w, new_h))
        
        # Create an empty RGBA canvas matching the user image
        canvas = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Calculate offset
        y_offset = face_bottom - int(new_h * 0.15) # Adjust collar to sit near chin
        x_offset = face_center - new_w // 2
        
        # Crop blazer if it goes out of bounds, and place on canvas
        y1, y2 = max(0, y_offset), min(h, y_offset + new_h)
        x1, x2 = max(0, x_offset), min(w, x_offset + new_w)
        
        b_y1 = 0 if y_offset >= 0 else -y_offset
        b_y2 = b_y1 + (y2 - y1)
        b_x1 = 0 if x_offset >= 0 else -x_offset
        b_x2 = b_x1 + (x2 - x1)
        
        canvas[y1:y2, x1:x2] = blazer_resized[b_y1:b_y2, b_x1:b_x2]
        
        # 4. Alpha blend the blazer over the user image
        alpha_channel = canvas[:, :, 3] / 255.0
        foreground = canvas[:, :, :3]
        
        result = user_img.copy()
        for c in range(3):
            result[:, :, c] = (alpha_channel * foreground[:, :, c] +
                               (1 - alpha_channel) * result[:, :, c])
                               
        return result

    def inpaint_region(self, image_bytes: bytes, mask: np.ndarray, plan: dict) -> np.ndarray:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        h, w = img.shape[:2]
        
        # 1. Replace background first
        bg = np.zeros((h, w, 3), dtype=np.uint8)
        
        color_tone = plan.get("color_tone", "professional").lower()
        bg_prompt = plan.get("background_prompt", "").lower()
        
        # Check if the user specifically asked for a clean professional background
        if "clean studio" in bg_prompt or "passport" in bg_prompt or "white" in bg_prompt:
            bg[:] = (240, 232, 226)
        else:
            # Use a free Text-to-Image API (Pollinations) to generate the requested background dynamically!
            logger.info("Dynamically generating AI background using text-to-image...")
            try:
                # We request a background without the person, so we add "empty background, scenery only"
                enh_prompt = f"Empty scenery, no people, {bg_prompt}"
                response = requests.get(f"https://image.pollinations.ai/prompt/{enh_prompt}?width={w}&height={h}&nologo=true", timeout=8)
                
                if response.status_code == 200:
                    bg_nparr = np.frombuffer(response.content, np.uint8)
                    bg_img = cv2.imdecode(bg_nparr, cv2.IMREAD_COLOR)
                    
                    if bg_img is not None:
                        # Resize just in case it didn't match perfectly
                        bg = cv2.resize(bg_img, (w, h))
                    else:
                        bg[:] = (255, 255, 255)
                else:
                    bg[:] = (255, 255, 255)
            except Exception as e:
                logger.warning(f"Failed to generate dynamic background: {e}")
                bg[:] = (255, 255, 255)
            
        mask_normalized = mask.astype(float) / 255.0
        if len(mask_normalized.shape) == 2:
            mask_normalized = np.expand_dims(mask_normalized, axis=2)
            
        result = (img * (1 - mask_normalized) + bg * mask_normalized).astype(np.uint8)
        
        # 2. Add clothing if requested
        clothing = plan.get("clothing", "none").lower()
        if "blazer" in clothing or "suit" in clothing:
            logger.info("Applying realistic AI-generated attire...")
            result = self.overlay_blazer(result, mask)
            
        return result

inpainter = GenerativeInpainter()
