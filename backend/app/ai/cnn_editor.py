import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance

try:
    from rembg import remove
except ImportError:
    remove = None

def apply_brightness_contrast(image, alpha=1.0, beta=0):
    # Alpha = contrast, Beta = brightness
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def apply_saturation(image, saturation_factor):
    # Convert to HSV, scale S channel, convert back
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Apply factor and clip to 0-255
    s = cv2.multiply(s, saturation_factor)
    s = np.clip(s, 0, 255).astype(np.uint8)
    
    hsv_new = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv_new, cv2.COLOR_HSV2BGR)

def auto_enhance(image):
    # Auto brightness/contrast using CLAHE on the L channel of LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced

def edit_image(image_bytes: bytes, instructions: dict, ann_params: dict = None) -> bytes:
    """
    CNN/CV Engine: Performs pixel-level manipulation based on NLP instructions.
    """
    # Load image with PIL
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # 1. Background Removal (CNN: U-Net via rembg)
    if instructions.get("remove_background") and remove:
        # rembg expects a PIL image and returns a transparent PNG
        pil_img = remove(pil_img)
    
    # Convert PIL to OpenCV format (numpy array)
    if pil_img.mode == 'RGBA':
        cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
    else:
        cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 2. OpenCV Facial/Subject Centering Logic for Portrait/ID Card
    if instructions.get("crop_portrait"):
        if hasattr(cv2, 'CascadeClassifier'):
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2GRAY) if cv_image.shape[2] == 4 else cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        else:
            # OpenCV 5+ removed CascadeClassifier; fallback to simple center crop
            faces = []
            
        if len(faces) > 0:
            x, y, w, h = faces[0]
            center_x, center_y = x + w // 2, y + h // 2
            target_w = int(w * 2.5)
            target_h = int(target_w * 4 / 3)
        else:
            # Simple center crop to 3:4 ratio if no face found or cascade unavailable
            h, w = cv_image.shape[:2]
            target_h = min(h, int(w * 4/3))
            target_w = int(target_h * 3/4)
            center_x, center_y = w // 2, h // 2
            
        x1 = max(0, center_x - target_w // 2)
        y1 = max(0, center_y - int(target_h * 0.4)) # Slightly higher than center
        x2 = min(cv_image.shape[1], x1 + target_w)
        y2 = min(cv_image.shape[0], y1 + target_h)
        
        cv_image = cv_image[y1:y2, x1:x2]

    # 3. Lighting Enhancement (CV/Filters)
    if instructions.get("enhance_lighting"):
        alpha = ann_params.get("contrast_alpha", 1.1) if ann_params else 1.1
        beta = ann_params.get("brightness_beta", 10.0) if ann_params else 10.0
        saturation = ann_params.get("saturation_gamma", 1.0) if ann_params else 1.0
        
        if cv_image.shape[2] == 4:
            b, g, r, a = cv2.split(cv_image)
            bgr = cv2.merge((b, g, r))
            
            # Apply CLAHE auto-enhancement first
            bgr = auto_enhance(bgr)
            
            # Apply brightness/contrast
            bgr = apply_brightness_contrast(bgr, alpha=alpha, beta=beta)
            # Apply saturation
            if saturation != 1.0:
                bgr = apply_saturation(bgr, saturation)
                
            b, g, r = cv2.split(bgr)
            cv_image = cv2.merge((b, g, r, a))
        else:
            cv_image = auto_enhance(cv_image)
            cv_image = apply_brightness_contrast(cv_image, alpha=alpha, beta=beta)
            if saturation != 1.0:
                cv_image = apply_saturation(cv_image, saturation)

    # 4. Add Backdrop if requested and background was removed
    if instructions.get("remove_background") and cv_image.shape[2] == 4: # Has alpha channel
        h, w = cv_image.shape[:2]
        bg = np.zeros((h, w, 3), dtype=np.uint8)
        
        style = instructions.get("style", "neutral")
        if style == "professional":
            # Professional blue-grey BGR
            bg[:] = (240, 232, 226) 
        elif style == "vibrant":
            # Bright warm gradient replacement (simplified as solid warm color for now)
            bg[:] = (100, 200, 255) # Yellow-orange
        else:
            # White background
            bg[:] = (255, 255, 255)
            
        alpha_channel = cv_image[:, :, 3] / 255.0
        foreground = cv_image[:, :, :3]
        
        for c in range(0, 3):
            bg[:, :, c] = (alpha_channel * foreground[:, :, c] +
                           (1 - alpha_channel) * bg[:, :, c])
        cv_image = bg

    # Convert back to bytes
    is_success, buffer = cv2.imencode(".png" if cv_image.shape[2] == 4 else ".jpg", cv_image)
    if not is_success:
        raise ValueError("Failed to encode image")
    
    return buffer.tobytes()
