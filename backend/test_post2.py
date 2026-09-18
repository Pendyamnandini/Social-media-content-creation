import requests

prompt = """You are a professional LinkedIn content creator AI. Generate a structured response for a LinkedIn post based on the user's input.
Topic/Input: attending an AI workshop
Content Type: Auto Detect
Tone: Professional
Audience: General
Length: Medium

Respond ONLY with a valid JSON object matching this schema. Do not include markdown formatting like ```json:
{
  "post": "The main linkedin post body",
  "hashtags": ["#Tag1", "#Tag2"],
  "suggestedComment": "A question or comment to start engagement",
  "suggestedMessage": "A private message to share this post"
}"""

payload={'messages':[{'role':'user','content':prompt}]}
print(requests.post('https://text.pollinations.ai/', json=payload).text)
