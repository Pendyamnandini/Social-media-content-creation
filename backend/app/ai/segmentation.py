import numpy as np
import cv2
import logging

try:
    from rembg import remove
except ImportError:
    remove = None

logger = logging.getLogger(__name__)

class SemanticSegmenter:
    """
    Semantic Segmentation: Analyzes and labels specific objects, textures, and regions.
    """
    def __init__(self):
        logger.info("Initializing Semantic Segmenter (SAM/U-Net Proxy)...")

    def generate_mask(self, image_bytes: bytes, target_object: str = "background") -> np.ndarray:
        """
        Generates a binary mask for the targeted object.
        """
        logger.info(f"Segmenting target: {target_object}")
        
        # Currently, we simulate advanced segmentation (like SAM) by using rembg for foreground/background segmentation.
        # In a full deployment, this would call Hugging Face Inference API for facebook/sam-vit-huge
        
        if target_object.lower() in ["background", "backdrop"] and remove:
            # Generate alpha mask using rembg
            output = remove(image_bytes, only_mask=True)
            # Convert bytes to numpy array
            nparr = np.frombuffer(output, np.uint8)
            mask = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            # rembg returns 255 for FOREGROUND and 0 for BACKGROUND.
            # Since we requested the "background" mask, we must invert it!
            mask = cv2.bitwise_not(mask)
            
            return mask
            
        else:
            # Fallback mock mask for other objects (just selects the center)
            # E.g., if user asks to "segment the cup"
            logger.warning(f"Semantic model for '{target_object}' not loaded locally. Using fallback mask.")
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            h, w = img.shape[:2]
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(mask, (w//2, h//2), min(w, h)//4, 255, -1)
            return mask

segmenter = SemanticSegmenter()
