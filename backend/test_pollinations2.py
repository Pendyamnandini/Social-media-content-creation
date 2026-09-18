import urllib.parse
import requests
prompt='Respond ONLY with a valid JSON object matching this schema. {"post": "hello", "hashtags": ["#tag"]} Topic: My new project'
print(requests.get(f'https://text.pollinations.ai/{urllib.parse.quote(prompt)}').text)