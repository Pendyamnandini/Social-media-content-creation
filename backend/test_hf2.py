import os
import requests
import base64
import io
from PIL import Image

HF_TOKEN = "your_huggingface_token"
API_URL = "https://router.huggingface.co/hf-inference/models/runwayml/stable-diffusion-inpainting"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def inpaint():
    # Make a red square
    img = Image.new('RGB', (512, 512), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_str = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    
    # Make a white square for the mask (white means replace)
    mask = Image.new('L', (512, 512), color = 'white')
    mask_byte_arr = io.BytesIO()
    mask.save(mask_byte_arr, format='JPEG')
    mask_str = base64.b64encode(mask_byte_arr.getvalue()).decode("utf-8")
        
    payload = {
        "inputs": "a photo of a professional dark blue blazer and light pink shirt",
        "parameters": {
            "image": img_str,
            "mask_image": mask_str
        }
    }
    
    print("Sending request...")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        with open("output.jpg", "wb") as f:
            f.write(response.content)
        print("Success! output.jpg saved.")
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    inpaint()
