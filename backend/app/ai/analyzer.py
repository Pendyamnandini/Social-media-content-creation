import logging
import json
import re
from app.ai.text_generation import text_service

logger = logging.getLogger(__name__)

class RequestAnalyzer:
    """
    Stage 1: Intent Analysis
    Takes the user's raw prompt and extracts structured intent using an LLM.
    """
    def __init__(self):
        pass

    def analyze(self, raw_input: str) -> dict:
        logger.info(f"Analyzing raw input: '{raw_input}'")
        
        prompt = (
            f"Analyze the following user request for an image generation/editing task.\n"
            f"Request: \"{raw_input}\"\n\n"
            f"Extract the following fields and return ONLY a JSON object: "
            f"task (image or video), style, platform, composition, background, clothing, aspect_ratio.\n"
            f"If a field is not specified, output 'auto'.\n"
            f"JSON format only:"
        )
        
        response_text = text_service.generate_text(prompt)
        
        # Parse JSON from LLM response
        intent = self._parse_json(response_text)
        logger.info(f"Extracted Intent: {intent}")
        return intent
        
    def _parse_json(self, text: str) -> dict:
        default_intent = {
            "task": "image",
            "style": "professional",
            "platform": "auto",
            "composition": "auto",
            "background": "clean",
            "clothing": "auto",
            "aspect_ratio": "auto"
        }
        
        try:
            # Find json block in text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                extracted = json.loads(json_str)
                # Merge with defaults to ensure all keys exist
                for k, v in extracted.items():
                    default_intent[k.lower()] = v.lower() if isinstance(v, str) else v
            else:
                # Basic fallback text-matching if JSON fails
                if "video" in text.lower() or "reel" in text.lower():
                    default_intent["task"] = "video"
                if "vibrant" in text.lower():
                    default_intent["style"] = "vibrant"
                if "blazer" in text.lower() or "suit" in text.lower():
                    default_intent["clothing"] = "professional suit"
                    
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON output: {e}. Using fallback.")
            
        return default_intent

analyzer = RequestAnalyzer()
