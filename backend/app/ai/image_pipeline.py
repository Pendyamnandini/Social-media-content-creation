import logging
import cv2
import numpy as np

from app.ai.segmentation import segmenter
from app.ai.inpainting import inpainter
from app.ai.harmonization import harmonizer

logger = logging.getLogger(__name__)

class ImageTaskPipeline:
    """
    Stage 4 & 5: Image Generation & Post-processing
    Executes the generation based on the optimized creative plan and applies post-processing.
    """
    def __init__(self):
        pass
        
    def process(self, image_bytes: bytes, intent: dict, creative_plan: str) -> bytes:
        logger.info("Executing ImageTaskPipeline...")
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        current_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 1. Semantic Segmentation
        # We always create a background mask for composition operations
        mask = segmenter.generate_mask(image_bytes, target_object="background")
        
        # 2. Inpainting (using the rich creative plan instead of the raw prompt)
        # The inpainter leverages our asset composition fallback or true API
        inpainted_bg = inpainter.inpaint_region(image_bytes, mask, creative_plan)
        
        # 3. Harmonization
        inv_mask = cv2.bitwise_not(mask)
        final_img = harmonizer.harmonize_composition(current_img, inpainted_bg, inv_mask)
        current_img = final_img
        
        # 4. Post-processing (Cropping, Sizing based on Platform)
        platform = intent.get("platform", "auto").lower()
        aspect_ratio = intent.get("aspect_ratio", "auto")
        
        # Automatically determine aspect ratio if platform is known
        if aspect_ratio == "auto":
            if "linkedin" in platform:
                aspect_ratio = "4:5"
            elif "instagram" in platform:
                aspect_ratio = "1:1"
            else:
                aspect_ratio = "3:4" # Default portrait
                
        # Apply intelligent crop
        h, w = current_img.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        if aspect_ratio == "1:1":
            target_size = min(h, w)
            y1 = max(0, center_y - target_size // 2)
            y2 = min(h, y1 + target_size)
            x1 = max(0, center_x - target_size // 2)
            x2 = min(w, x1 + target_size)
            current_img = current_img[y1:y2, x1:x2]
            
        elif aspect_ratio == "4:5": # LinkedIn standard portrait
            target_h = min(h, int(w * 5/4))
            target_w = int(target_h * 4/5)
            y1 = max(0, center_y - int(target_h * 0.45))
            y2 = min(h, y1 + target_h)
            x1 = max(0, center_x - target_w // 2)
            x2 = min(w, x1 + target_w)
            current_img = current_img[y1:y2, x1:x2]
            
        # 5. Quality Evaluation (Placeholder for scoring system)
        logger.info("Quality evaluation passed (Simulated).")

        # Encode and return
        is_success, buffer = cv2.imencode(".jpg", current_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not is_success:
            raise ValueError("Failed to encode final image")
            
        logger.info("--- ImageTaskPipeline Complete ---")
        return buffer.tobytes()
