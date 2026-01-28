# settings.py
import os
import json
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)


def env_str(name: str, default: str = "") -> str:
    v = os.getenv(name, default)
    if v is None:
        return default
    return v.strip().strip('"').strip("'").lstrip("\ufeff")


try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ===== Required =====
OPENAI_API_KEY = env_str("OPENAI_API_KEY")
HAS_KEY = bool(OPENAI_API_KEY)

APP_SECRET = env_str("APP_SECRET", "dev-secret-change-me")

# ===== Optional =====
APP_USERS_JSON = env_str("APP_USERS_JSON", "")
USERS: Dict[str, str] = {}
if APP_USERS_JSON:
    try:
        parsed = json.loads(APP_USERS_JSON)
        if isinstance(parsed, dict):
            USERS = {str(k).lower(): str(v) for k, v in parsed.items()}
    except Exception:
        USERS = {}

REALTIME_MODEL = env_str("REALTIME_MODEL", "gpt-realtime-mini")
ASR_MODEL = env_str("ASR_MODEL", "gpt-4o-mini-transcribe")
ASR_LANGUAGE = env_str("ASR_LANGUAGE", "")  # "" => omit => auto-detect
VOICE = env_str("VOICE", "marin")

COACH_MODEL = env_str("COACH_MODEL", "gpt-4o-mini")
GRADER_MODEL = env_str("GRADER_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if (HAS_KEY and OpenAI is not None) else None

ONBOARDING = {
    "pdf_url": "/static/onboarding.pdf",
    "video_url": "https://youtu.be/fPXruR7bgsk?si=M6nCV1HOUv6etpv1",
}
