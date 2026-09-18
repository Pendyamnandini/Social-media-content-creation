import os
import requests
import logging
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class PollinationsTextProvider(AIProvider):
    def __init__(self):
        self.api_url = "https://text.pollinations.ai/"
        
    def generate(self, prompt: str) -> str:
        logger.info("Generating text via Pollinations.ai (GET API)")
        try:
            import urllib.parse
            # Use GET endpoint which has fewer restrictions for free use
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.api_url}{encoded_prompt}?json=true"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text.strip()
            else:
                logger.error(f"Pollinations API Error {response.status_code}: {response.text}")
                raise RuntimeError(f"API Error: {response.status_code}")
        except Exception as e:
            logger.error(f"Pollinations API exception: {str(e)}")
            raise

class HuggingFaceProvider(AIProvider):
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        self.model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        
    def generate(self, prompt: str) -> str:
        if not self.token:
            raise RuntimeError("HF_TOKEN not found in environment.")
        logger.info(f"Generating text via HuggingFace API ({self.model})")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        # Wrap prompt in Mistral instruct format for better results
        formatted_prompt = f"[INST] {prompt} [/INST]"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {"max_new_tokens": 1024, "temperature": 0.7, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return result[0]["generated_text"].strip()
            return str(result)
        else:
            logger.error(f"HF API Error {response.status_code}: {response.text}")
            raise RuntimeError(f"HF API Error: {response.status_code}")

class FallbackProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        logger.info("Using FallbackProvider for text generation.")
        return "This is a fallback generated response. The primary AI provider is currently unavailable or skipped."

class TextGenerationService:
    def __init__(self):
        self.providers = []
        
        # Primary Provider: Pollinations (GET endpoint)
        self.providers.append(PollinationsTextProvider())
            
        # Backup Provider
        self.providers.append(FallbackProvider())
        
    def generate_text(self, prompt: str) -> str:
        """Generic text generation method that routes through the provider fallback chain."""
        for provider in self.providers:
            try:
                result = provider.generate(prompt)
                if result:
                    return result
            except Exception as e:
                print(f"ERROR: {e}")
                logger.warning(f"Provider {provider.__class__.__name__} failed, falling back... ({e})")
        return "Fallback text generated due to provider failures."

    def generate_content(self, topic: str, platform: str, tone: str) -> dict:
        prompt = (
            f"You are an expert Social Media Manager. Deeply understand the core message, intent, and emotions in the following topic. "
            f"Create a highly engaging, creative, and professional {tone} post for {platform} that tells a story and captures attention. Do not just paraphrase. "
            "Also, create a highly detailed, creative, and dynamic text-to-image prompt (no text/words in the image) that visually represents the core message of the topic. The image style should match the topic (e.g., celebratory for achievements, futuristic for tech, event-style for workshops). "
            "Respond ONLY with a valid JSON object matching this schema exactly: "
            '{"post_text": "The highly engaging post text", "image_prompt": "The dynamic visual concept prompt", "hashtags": ["#tag1", "#tag2"]}. '
            f"Topic: {topic}"
        )
        
        response_text = self.generate_text(prompt)
        
        try:
            import json, re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = {"post_text": response_text, "image_prompt": f"A highly detailed, professional, and creative visual conceptualizing: {topic}. No text.", "hashtags": [f"#{platform}", "#PostCraftAI"]}
        except Exception:
            data = {"post_text": response_text, "image_prompt": f"A highly detailed, professional, and creative visual conceptualizing: {topic}. No text.", "hashtags": [f"#{platform}", "#PostCraftAI"]}
            
        post_text = data.get("post_text", response_text)
        image_prompt = data.get("image_prompt", f"A highly detailed, professional, and creative visual conceptualizing: {topic}. No text.")
        hashtags = data.get("hashtags", [f"#{platform}", "#PostCraftAI"])
        
        import urllib.parse
        safe_prompt = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true&width=1024&height=1024"
        
        return {
            "post_text": post_text,
            "visual_concept": image_prompt,
            "image_url": image_url,
            "hashtags": hashtags,
            "recommended_time": "Today at 5:00 PM (Optimal for engagement)",
            "ai_suggestion": "Consider asking a direct question to your audience at the end of the post to boost comments."
        }

text_service = TextGenerationService()
