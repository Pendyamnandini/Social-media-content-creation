import logging
from app.ai.text_generation import text_service

logger = logging.getLogger(__name__)

class CreativePlanner:
    """
    Stage 2: Creative / Prompt Planner
    Translates the analyzed intent into a detailed production instruction or Stable Diffusion prompt.
    """
    def __init__(self):
        pass

    def create_plan(self, intent: dict, raw_input: str) -> dict:
        logger.info(f"Creating creative plan for intent: {intent}")
        
        prompt = (
            f"You are an expert AI production planner. Convert this user request into a strict editing plan.\n"
            f"Intent: {intent}\n"
            f"Original user request: '{raw_input}'\n\n"
            f"You MUST return ONLY a valid JSON object with the following keys:\n"
            f"- 'background_prompt': A highly detailed, purely descriptive prompt for generating the background environment (e.g. 'A lush blooming garden with colorful flowers, bright sunlight, highly detailed landscape'). DO NOT mention people or the user in this prompt, just the background scenery.\n"
            f"- 'clothing': If they asked for specific professional clothing, output 'blazer' or 'suit', otherwise 'none'.\n"
            f"- 'color_tone': 'professional' (for clean/corporate) or 'vibrant' (for social media/creative).\n"
        )
        
        response = text_service.generate_text(prompt)
        
        # Parse JSON from response
        plan = {
            "background_prompt": "A clean studio background",
            "clothing": "none",
            "color_tone": "professional"
        }
        try:
            import re, json
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                extracted = json.loads(match.group(0))
                plan.update(extracted)
        except Exception as e:
            logger.warning(f"Failed to parse planner JSON: {e}")
            # Fallback based on raw intent
            if intent.get("background") and intent.get("background") != "auto":
                plan["background_prompt"] = intent["background"]
            
        logger.info(f"Creative Plan generated: {plan}")
        return plan

planner = CreativePlanner()
