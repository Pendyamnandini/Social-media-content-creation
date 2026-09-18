import os
import requests
token='your_huggingface_token'
url='https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2'
headers={'Authorization': f'Bearer {token}'}
res=requests.post(url, headers=headers, json={'inputs': 'Write a professional linkedin post about AI'})
print(res.json())
