# openai_realtime.py
import json
import requests

from settings import env_str, REALTIME_MODEL, ASR_MODEL, ASR_LANGUAGE, VOICE


def webrtc_answer_sdp(offer_sdp: str, instructions: str) -> str:
    """
    Sends a browser SDP offer to OpenAI Realtime and returns the SDP answer.
    Uses multipart form-data fields: sdp + session
    """
    api_key = env_str("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in .env and restart.")

    if not offer_sdp:
        raise RuntimeError("Empty SDP offer")
    if not offer_sdp.startswith("v=0"):
        raise RuntimeError(f"Bad SDP offer. First 80 chars: {offer_sdp[:80]!r}")
    if not offer_sdp.endswith("\n"):
        offer_sdp += "\n"

    url = "https://api.openai.com/v1/realtime/calls"
    headers = {"Authorization": f"Bearer {api_key}"}

    audio_input = {"transcription": {"model": ASR_MODEL}}
    # If ASR_LANGUAGE is set, pass it; otherwise omit to allow auto-detect
    if ASR_LANGUAGE:
        audio_input["transcription"]["language"] = ASR_LANGUAGE

    session = {
        "type": "realtime",
        "model": REALTIME_MODEL,
        "instructions": instructions,
        "audio": {
            "input": audio_input,
            "output": {"voice": VOICE},
        },
    }

    files = {
        "sdp": (None, offer_sdp, "application/sdp"),
        "session": (None, json.dumps(session), "application/json"),
    }

    resp = requests.post(url, headers=headers, files=files, timeout=60)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"OpenAI realtime error {resp.status_code}: {resp.text}")

    return resp.text
