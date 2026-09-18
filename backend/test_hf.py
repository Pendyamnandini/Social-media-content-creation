import sys
import os

# Add backend dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.text_generation import text_service

print(text_service.generate_text('Give me a JSON object with a single key "test" and value 1'))
