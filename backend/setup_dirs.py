import os

base_path = r"D:\socialpilot-ai\backend\app"
dirs = [
    "config", "api", "models", "schemas", "services", "repositories",
    "ai", "ml", "nlp", "recommendations", "integrations", "scheduling",
    "analytics", "security", "utils", "tests"
]

for d in dirs:
    path = os.path.join(base_path, d)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "__init__.py"), "w") as f:
        pass

# Create empty alembic dir
os.makedirs(r"D:\socialpilot-ai\backend\alembic\versions", exist_ok=True)
