import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_ROOT / "marksheet_extractor.db"
ENV_PATH = WORKSPACE_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)

APP_NAME = "Marksheet AI"
APP_SUBTITLE = "Enterprise Marksheet Extraction & Academic Analytics"
APP_VERSION = "2.4.0"
USER_DISPLAY_NAME = "Harshanth"
COPYRIGHT_NAME = "duvvuruharshanthreddy"

# Upload Limits & Supported Types
MAX_FILE_SIZE_MB = 25
MAX_FILES_BATCH = 10
SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf"]

# Supported Vision Models on Groq
GROQ_MODELS = [
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "qwen/qwen3.8-27b"
]
DEFAULT_GROQ_MODEL = "llama-3.2-11b-vision-preview"

# Default API backend URL
DEFAULT_BACKEND_URL = "http://localhost:8000"
FALLBACK_RENDER_URL = "https://marksheet-extractor-ciik.onrender.com"

# Extraction Engines
ENGINE_OFFLINE = "⚡ Local OCR / Document Engine"
ENGINE_GROQ = "🤖 Groq Vision AI (Multimodal LLM)"
ENGINE_BACKEND = "🌐 Backend API Service"
ENGINES = [ENGINE_OFFLINE, ENGINE_GROQ, ENGINE_BACKEND]

# Default Grading System Config
DEFAULT_PASSING_PERCENTAGE = 40.0
DEFAULT_DISTINCTION_PERCENTAGE = 75.0
DEFAULT_MAX_MARKS = 100.0


def get_api_key(key_name: str = "GROQ_API_KEY") -> str:
    """Retrieve API key from environment safely without crashing"""
    return os.getenv(key_name, "").strip()


def save_api_key(api_key: str, key_name: str = "GROQ_API_KEY") -> bool:
    """Save API key to .env file in workspace root"""
    try:
        lines = []
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

        key_found = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key_name}="):
                new_lines.append(f"{key_name}={api_key.strip()}\n")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"{key_name}={api_key.strip()}\n")

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        os.environ[key_name] = api_key.strip()
        return True
    except Exception:
        return False
