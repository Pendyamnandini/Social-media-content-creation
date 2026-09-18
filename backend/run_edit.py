import sys
import os
import io

# Setup path so we can import from app
sys.path.append('d:/socialpilot-ai/backend')

from app.ai.nlp_processor import parse_edit_instructions
from app.ai.ann_recommender import ann_recommender
from app.ai.cnn_editor import edit_image

def process_user_image(image_path: str, instructions: str, output_path: str):
    print("Reading image...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    print(f"Parsing instructions: '{instructions}'")
    intent = parse_edit_instructions(instructions)
    print("Intent:", intent)
    
    print("Getting ANN params...")
    ann_params = ann_recommender.predict_parameters(
        style=intent.get("style", "neutral"),
        platform="linkedin"
    )
    print("ANN Params:", ann_params)
    
    print("Running CNN editing...")
    res_bytes = edit_image(image_bytes, intent, ann_params)
    
    with open(output_path, "wb") as f:
        f.write(res_bytes)
    print(f"Done! Saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 3:
        process_user_image(sys.argv[1], sys.argv[2], sys.argv[3])
