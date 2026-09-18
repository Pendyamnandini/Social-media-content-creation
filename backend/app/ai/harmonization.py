import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class HarmonizationEngine:
    """
    Latent Feature Extraction & Harmonization: 
    Recalculates lighting, scale, and shadows so added elements blend naturally.
    """
    def __init__(self):
        logger.info("Initializing Harmonization Engine...")

    def extract_latent_lighting(self, image: np.ndarray):
        """
        Extracts global lighting and color vectors.
        """
        # Convert to LAB to extract luminance
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        mean_l = np.mean(l)
        mean_a = np.mean(a)
        mean_b = np.mean(b)
        return mean_l, mean_a, mean_b

    def harmonize_composition(self, foreground: np.ndarray, background: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Context & Physics Matching: Matches the lighting of the foreground to the new background.
        """
        logger.info("Harmonizing foreground and background...")
        
        # In a latent model, this is done via cross-attention. 
        # Locally, we simulate this via color transfer (Reinhard et al.)
        
        fg_l, fg_a, fg_b = self.extract_latent_lighting(foreground)
        bg_l, bg_a, bg_b = self.extract_latent_lighting(background)
        
        # Color match foreground to background slightly to harmonize
        lab_fg = cv2.cvtColor(foreground, cv2.COLOR_BGR2LAB).astype(np.float32)
        l, a, b = cv2.split(lab_fg)
        
        # Shift means
        l = l - fg_l + bg_l * 0.5 + fg_l * 0.5 # 50% blend
        a = a - fg_a + bg_a * 0.2 + fg_a * 0.8
        b = b - fg_b + bg_b * 0.2 + fg_b * 0.8
        
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)
        
        harmonized_lab = cv2.merge((l, a, b)).astype(np.uint8)
        harmonized_fg = cv2.cvtColor(harmonized_lab, cv2.COLOR_LAB2BGR)
        
        # Blend
        mask_normalized = mask.astype(float) / 255.0
        if len(mask_normalized.shape) == 2:
            mask_normalized = np.expand_dims(mask_normalized, axis=2)
            
        final = (harmonized_fg * mask_normalized + background * (1 - mask_normalized)).astype(np.uint8)
        return final

harmonizer = HarmonizationEngine()
