import json
import logging
from app.ai.text_generation import text_service
import random
import urllib.parse
import re

logger = logging.getLogger(__name__)

class LinkedInAIService:
    
    def generate_content(self, prompt: str, image_description: str, content_type: str, tone: str, audience: str, length: str) -> dict:
        """Generates LinkedIn content, image prompt, and extracts metadata in a single structured LLM call."""
        
        system_prompt = f"""You are an elite, natural-language AI Social Media Expert.
Your primary task is to deeply understand the context, intent, key themes, emotions, and purpose of the user's prompt, and creatively transform it into a highly engaging, professional, and publish-ready social media post. Do not merely paraphrase the prompt.

USER PROMPT:
"{prompt}"

USER IMAGE DESCRIPTION:
"{image_description if image_description else 'No specific instructions provided.'}"

SELECTED UI OPTIONS:
- Content Type: {content_type}
- Tone: {tone}
- Audience: {audience}
- Length: {length}

CRITICAL RULES FOR CONTENT GENERATION:
1. DEEP UNDERSTANDING & CREATIVITY: First, identify important concepts (e.g., event, technology, milestone, emotion). Build a compelling narrative around these concepts. Do not just rewrite the user's sentence. 
2. ENGAGEMENT & STRUCTURE: Create a powerful, engaging hook/opening. Highlight the core idea. Use storytelling where appropriate. Ensure visual readability with proper spacing and structure. Adapt the style dynamically to the topic.
3. TONE & HUMANITY: Make the content feel like an authentic, human-written post. Include emotional or relatable elements when suitable. Use appropriate emojis (do not overuse them). Avoid repetitive AI buzzwords and generic openings (like "I am thrilled to announce" or "I recently focused on").
4. AVOID REPETITION: Vary hooks, sentence structures, storytelling patterns, formatting, and CTA styles. Do not generate the same style every time.
5. FACT PRESERVATION (MAINTAIN USER INTENT): DO NOT invent important facts, rankings, dates, or results that were not provided. You can creatively present the information, but preserve the actual factual meaning of the original prompt.
6. MENTIONS: Extract requested tags. Mention them naturally in the text and list them in the "requested_mentions" array.
7. DYNAMIC IMAGE GENERATION: If the USER IMAGE DESCRIPTION is provided, you MUST prioritize it to generate the `imagePrompt`. Include their requested subject, objects, colors, and style in the final prompt. If USER IMAGE DESCRIPTION is empty/not provided, dynamically infer an appropriate visual concept from the USER PROMPT (e.g., celebratory for achievements, futuristic for tech). Ensure the `imagePrompt` is highly detailed, modern, relevant, visually attractive, and contains NO text/words.
8. Make sure the 'analysis' field matches the specified detailed internal data model schema below exactly. Extract only what is provided; leave null or empty if not provided.

Respond ONLY with a valid JSON object matching this exact schema (no markdown formatting):
{{
  "post": "The complete, highly engaging social media post text, following the structural and creative rules above.",
  "hashtags": ["#RelevantTag1", "#CreativeTag2"],
  "suggestedComment": "A natural, conversation-starting comment for the author to post.",
  "suggestedMessage": "A professional private message snippet to share this post.",
  "imagePrompt": "A highly specific, creative, text-to-image prompt tailored exactly to the meaning and mood of the post (e.g., futuristic, celebratory, event-style). Cinematic lighting, professional, no text.",
  "requested_mentions": ["Name 1", "Name 2"],
  "analysis": {{
    "original_prompt": "{prompt}",
    "event": {{
      "name": "...",
      "date": "...",
      "location": "...",
      "organization": "..."
    }},
    "project": {{
      "name": "...",
      "description": "...",
      "technologies": []
    }},
    "user_contribution": "...",
    "people": [
      {{
        "name": "...",
        "thank": true,
        "tag_requested": true
      }}
    ],
    "tone": "...",
    "audience": "...",
    "content_instructions": [],
    "image_instructions": [],
    "image_concepts": [],
    "hashtags": {{
      "count": null,
      "instructions": []
    }}
  }}
}}
"""
        try:
            response_text = text_service.generate_text(system_prompt)
            
            # Clean up potential markdown formatting from AI output
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_text = json_match.group(0)
            else:
                raise ValueError("No JSON object found in response")
                
            data = json.loads(response_text)
            
            # Add metadata
            data["contentType"] = content_type
            data["tone"] = tone
            data["audience"] = audience
            
            # Ensure analysis exists for refresh requests
            if "analysis" not in data:
                data["analysis"] = {"original_prompt": prompt}
                
            image_prompt = data.get("imagePrompt", f"A professional conceptual photo related to: {prompt}")
            prompt_encoded = urllib.parse.quote(image_prompt)
            data["imageUrl"] = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn content: {e}")
            
            # ADVANCED FALLBACK NLP ENGINE
            # This executes when external LLMs are rate-limited or DNS blocked.
            
            text = prompt.strip()
            
            # 1. Grammar and pronoun correction
            replacements = {
                " i ": " I ", " i've ": " I've ", " i'm ": " I'm ", " i'll ": " I'll ",
                " mango db": "MongoDB", " Mango db": "MongoDB", " Mango DB": "MongoDB",
                " ai ": " AI ", " ml ": " ML ", " Ai ": " AI ", " Ml ": " ML ",
                " .": ".", " ,": ",", " !": "!"
            }
            for k, v in replacements.items():
                text = text.replace(k, v)
                
            if text and text[0].islower():
                text = text[0].upper() + text[1:]
                
            # 2. Extract Event/Project keywords for image generation
            stop_words = {"today", "yesterday", "attended", "went", "to", "a", "an", "the", "which", "is", "based", "on", "and", "i", "have", "learnt", "learned", "so", "many", "things", "met", "people", "made", "connections", "it", "was", "very", "much", "interesting", "session", "workshop", "meetup", "hackathon"}
            words = [w.strip('.,!') for w in text.lower().split() if len(w) > 2]
            topic_keywords = [w for w in words if w not in stop_words]
            topic = " ".join(topic_keywords[:5]) if topic_keywords else "technology and networking"
            
            # 3. Rewrite sentence dynamically to sound professional
            # Detect if it's an event/meetup
            is_event = any(w in text.lower() for w in ["workshop", "meetup", "hackathon", "conference", "event"])
            
            if is_event:
                if tone == "Professional":
                    body = f"I recently had the incredible opportunity to attend an insightful event focused on {topic}.\n\n"
                    body += f"Reflecting on the experience: {text}\n\n"
                    body += "It’s always inspiring to connect with like-minded professionals and learn about the latest advancements in the industry. Looking forward to applying these insights in upcoming projects! 🚀"
                else:
                    body = f"Just wrapped up an amazing session on {topic}! 💡\n\n"
                    body += f"{text}\n\n"
                    body += "Constantly pushing boundaries and meeting new people is what keeps this journey so exciting. Can't wait for what's next!"
            else:
                body = f"I've been diving deep into {topic} recently.\n\n"
                body += f"{text}\n\n"
                body += "Every new challenge brings a fresh perspective. I'm excited to continue this learning journey and share more updates soon! ✨"
            
            if length == "Detailed":
                body += "\n\nWhen we step out of our comfort zones and embrace new challenges, we discover so much more about our potential and the power of collaboration. The future is built by those willing to keep exploring and innovating."
            
            # Format requested mentions if any exist in the prompt (e.g. "@John Doe")
            mentions = [word.strip('.,!') for word in text.split() if word.startswith('@')]
            
            image_prompt = f"A high-quality, realistic, professional, creative image illustrating: {topic}. Cinematic lighting, no text, highly detailed."
            prompt_encoded = urllib.parse.quote(image_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
            
            return {
                "post": body,
                "hashtags": ["#LinkedIn", "#ProfessionalGrowth", "#Innovation", "#Networking", "#Tech"],
                "suggestedComment": "What are your thoughts on this? Let me know in the comments!",
                "suggestedMessage": "Hi! I just shared a new update and would love to hear your thoughts.",
                "contentType": content_type,
                "tone": tone,
                "audience": audience,
                "imageUrl": image_url,
                "analysis": {"original_prompt": prompt, "event": "Professional Event", "project": "Learning & Networking"},
                "imagePrompt": image_prompt,
                "requested_mentions": mentions
            }

    def regenerate_image(self, analysis_json: str, previous_image_prompt: str = None) -> str:
        """Regenerates an image using existing content analysis or previous image prompt."""
        try:
            analysis = json.loads(analysis_json) if analysis_json else {}
        except:
            analysis = {}
            
        # Use the provided previous prompt or fall back to analysis
        image_prompt = previous_image_prompt
        if not image_prompt:
            # Fallback for older posts that might not have imagePrompt passed directly
            image_prompt = analysis.get("original_prompt", "Professional LinkedIn post visualization")
            
        seed = random.randint(1, 1000000)
        prompt_encoded = urllib.parse.quote(image_prompt)
        return f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true&seed={seed}"

linkedin_ai_service = LinkedInAIService()
