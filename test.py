import requests, urllib.parse

prompt = "Return a JSON object with key 'status' and value 123. Respond ONLY with JSON, no markdown."
url = "https://text.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
res = requests.get(url)
print(res.text)
