import logging
import cv2
import numpy as np

from app.ai.nlp_processor import parse_edit_instructions
from app.ai.segmentation import segmenter
from app.ai.inpainting import inpainter
from app.ai.harmonization import harmonizer

logger = logging.getLogger(__name__)

class GenerativePipeline:
    """
    Orchestrates the entire Multi-Image Composition & Progressive Iteration workflow.
    """
    def __init__(self):
        pass
        
    def process(self, image_bytes: bytes, instructions: str) -> bytes:
        logger.info("--- Starting Advanced Generative Pipeline ---")
        
        # 1. Natural Language Processing (NLP)
        intent = parse_edit_instructions(instructions)
        logger.info(f"Parsed Intent: {intent}")
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        current_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 2. Semantic Segmentation
        if intent.get("remove_background") or intent.get("style") in ["vibrant", "cinematic"]:
            mask = segmenter.generate_mask(image_bytes, target_object="background")
            
            # 3. Inpainting & Latent Feature Extraction
            prompt = instructions if intent.get("style") != "neutral" else "clean background"
            inpainted_bg = inpainter.inpaint_region(image_bytes, mask, prompt)
            
            # 4. Embedding Layers and Harmonization
            # We treat the original image as foreground and the inpainted region as background
            inv_mask = cv2.bitwise_not(mask)
            final_img = harmonizer.harmonize_composition(current_img, inpainted_bg, inv_mask)
            current_img = final_img
            
        # Add basic OpenCV crop if requested
        if intent.get("crop_portrait") and not any(word in instructions.lower() for word in ["blazer", "suit", "shirt"]):
            # Simple center crop for demonstration
            h, w = current_img.shape[:2]
            target_h = min(h, int(w * 4/3))
            target_w = int(target_h * 3/4)
            center_x, center_y = w // 2, h // 2
            
            y1 = max(0, center_y - int(target_h * 0.4))
            y2 = min(current_img.shape[0], y1 + target_h)
            x1 = max(0, center_x - target_w // 2)
            x2 = min(current_img.shape[1], x1 + target_w)
            current_img = current_img[y1:y2, x1:x2]

        is_success, buffer = cv2.imencode(".jpg", current_img)
        if not is_success:
            raise ValueError("Failed to encode final generative image")
            
        logger.info("--- Generative Pipeline Complete ---")
        return buffer.tobytes()

generative_pipeline = GenerativePipeline()
