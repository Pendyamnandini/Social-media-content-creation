from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        logger.info("Initializing NLP model...")
        self.classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
        self.candidate_labels = [
            "remove background", 
            "enhance lighting", 
            "crop to portrait",
            "professional style",
            "vibrant style",
            "cinematic style"
        ]
        logger.info("NLP model loaded.")

    def parse_edit_instructions(self, instruction_text: str):
        if not instruction_text:
            return {
                "remove_background": False,
                "enhance_lighting": False,
                "crop_portrait": False,
                "style": "neutral"
            }
            
        result = self.classifier(instruction_text, self.candidate_labels, multi_label=True)
        
        actions = {
            "remove_background": False,
            "enhance_lighting": False,
            "crop_portrait": False,
            "style": "neutral"
        }
        
        # Log for debugging
        logger.info(f"NLP Labels: {result['labels']}")
        logger.info(f"NLP Scores: {result['scores']}")
        
        for label, score in zip(result['labels'], result['scores']):
            if score > 0.4:
                if label == "remove background":
                    actions["remove_background"] = True
                elif label == "enhance lighting":
                    actions["enhance_lighting"] = True
                elif label == "crop to portrait":
                    actions["crop_portrait"] = True
                elif label == "professional style" and score > 0.5:
                    actions["style"] = "professional"
                elif label == "vibrant style" and score > 0.5:
                    actions["style"] = "vibrant"
                elif label == "cinematic style" and score > 0.5:
                    actions["style"] = "cinematic"

        # Hardcode some simple rules to cover style based on instructions to be absolutely certain
        lower_text = instruction_text.lower()
        if "professional" in lower_text or "id card" in lower_text or "linkedin" in lower_text:
            actions["remove_background"] = True
            actions["enhance_lighting"] = True
            actions["crop_portrait"] = True
            actions["style"] = "professional"
        
        if "vibrant" in lower_text or "instagram" in lower_text or "colorful" in lower_text:
            actions["enhance_lighting"] = True
            actions["style"] = "vibrant"
            
        if "cinematic" in lower_text or "dramatic" in lower_text:
            actions["enhance_lighting"] = True
            actions["style"] = "cinematic"
            
        if "remove background" in lower_text or "clear background" in lower_text or "cut out" in lower_text:
            actions["remove_background"] = True

        return actions

_nlp_processor = None

def parse_edit_instructions(instruction_text: str):
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor()
    return _nlp_processor.parse_edit_instructions(instruction_text)
