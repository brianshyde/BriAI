from huggingface_hub import HfApi
import os

# === CONFIG ===
FOLDER = "genai_project"           # your project folder
SPACE = "BrianTek-5/BrianTechAI"   # your HF Space
# ==============

api = HfApi()

print(f"Uploading '{FOLDER}' to space '{SPACE}'...")

api.upload_folder(
    folder_path=FOLDER,
    repo_id=SPACE,
    repo_type="space",
    commit_message="Deploy Gradio app (large folder)",
    # No chunk_size → use default (smart streaming)
    ignore_patterns=[
        "__pycache__",
        "*.pyc",
        ".git",
        ".venv",
        "outputs/",
        "cache/",
        "*.log"
    ]
)

print("SUCCESS! Upload complete.")
print("Now run: gradio deploy")
