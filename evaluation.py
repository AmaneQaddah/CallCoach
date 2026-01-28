# evaluation.py
import json
import re
from typing import Dict, Any, List, Optional

from settings import client, COACH_MODEL, GRADER_MODEL
from prompts import COACH_SYSTEM_PROMPT, GRADER_RUBRIC, CHECKLIST_SYSTEM_PROMPT


def _extract_recent_context(transcript: str, max_lines: int = 14) -> str:
    lines = [ln.strip() for ln in (transcript or "").splitlines() if ln.strip()]
    tail = lines[-max_lines:]
    return "\n".join(tail)[-2400:]


def _agent_only(transcript: str) -> str:
    lines = [ln.strip() for ln in (transcript or "").splitlines() if ln.strip()]
    agent_lines = [ln for ln in lines if ln.upper().startswith("AGENT:")]
    return "\n".join(agent_lines)


def _has_customer(transcript: str) -> bool:
    t = (transcript or "").upper()
    return "CUSTOMER:" in t


def _script_state(transcript: str) -> dict:
    a = _agent_only(transcript).lower()

    opening_done = bool(
        re.search(r"\b(my name is|this is)\b", a)
        and re.search(r"\b(team|support|from|company)\b", a)
        and re.search(r"\bhow can i help\b", a)
    )

    # Identification / verification (asked for name/id/last4/phone/email)
    identification_done = bool(
        re.search(r"\b(name|last\s*(4|four)|id|phone|phone number|email)\b", a)
    )

    empathy_done = bool(
        re.search(r"\b(i understand|i'm sorry|sorry to hear|that sounds|i can imagine|i appreciate)\b", a)
    )

    clarify_done = bool(
        re.search(r"\b(can you|could you|may i|what|when|where|which|how)\b", a)
        or "?" in a
    )

    restate_done = bool(
        re.search(r"\b(just to confirm|to confirm|to make sure i understand|if i understand|so you('re| are))\b", a)
    )

    expectations_done = bool(
        re.search(r"\b(next step|what i('ll| will) do|i('ll| will) (check|look|review|open|create|email|call)|within|today|tomorrow|minutes|hours|by (the end|eod))\b", a)
    )

    close_done = bool(re.search(r"\b(to summarize|just to summarize|summary|recap)\b", a))

    feedback_done = bool(re.search(r"\b(survey|feedback|rate|rating)\b", a))

    near_closing = bool(re.search(r"\b(anything else|have a (good|nice) day|goodbye|bye|thank you for calling)\b", a))

    return {
        "opening_done": opening_done,
        "identification_done": identification_done,
        "empathy_done": empathy_done,
        "clarify_done": clarify_done,
        "restate_done": restate_done,
        "expectations_done": expectations_done,
        "close_done": close_done,
        "feedback_done": feedback_done,
        "near_closing": near_closing,
    }


def _next_missing_step(state: dict, transcript: str) -> Optional[str]:
    # Prefer one next action (lowest cognitive load)
    if not state["opening_done"]:
        return "opening"

    # Early script: identification (optional but recommended)
    if _has_customer(transcript) and not state["identification_done"]:
        return "verification"

    if _has_customer(transcript) and not state["empathy_done"]:
        return "empathy"

    if _has_customer(transcript) and not state["clarify_done"]:
        return "clarify"

    if _has_customer(transcript) and not state["restate_done"]:
        return "restate"

    if _has_customer(transcript) and not state["expectations_done"]:
        return "plan"

    if state["near_closing"]:
        if not state["close_done"]:
            return "close"
        if not state["feedback_done"]:
            return "survey"

    return None


def coach_tips(transcript: str) -> Dict[str, Any]:
    if client is None:
        return {"should_intervene": False, "tip": "", "reason_tag": "missing_key", "urgency": "low"}

    state = _script_state(transcript)
    missing = _next_missing_step(state, transcript)

    if not missing:
        return {"should_intervene": False, "tip": "", "reason_tag": "other", "urgency": "low"}

    focus = _extract_recent_context(transcript)

    user_msg = (
        "Call-script status (True/False):\n"
        f"- opening={state['opening_done']}\n"
        f"- identification={state['identification_done']}\n"
        f"- empathy={state['empathy_done']}\n"
        f"- clarify={state['clarify_done']}\n"
        f"- restate={state['restate_done']}\n"
        f"- expectations={state['expectations_done']}\n"
        f"- close={state['close_done']}\n"
        f"- feedback={state['feedback_done']}\n"
        f"Next missing step to coach NOW: {missing}\n\n"
        f"Transcript (recent):\n{focus}"
    )

    r = client.responses.create(
        model=COACH_MODEL,
        input=[
            {"role": "system", "content": COACH_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_output_tokens=160,
    )

    txt = (r.output_text or "").strip()
    try:
        data = json.loads(txt)
    except Exception:
        return {"should_intervene": False, "tip": "", "reason_tag": "parse_error", "urgency": "low"}

    tip = str(data.get("tip") or "").strip()
    words = tip.split()
    if len(words) > 14:
        tip = " ".join(words[:14])

    reason = str(data.get("reason_tag") or missing or "other").strip().lower()
    allowed = {
        "opening", "verification", "empathy", "clarify", "restate", "plan", "close", "survey",
        "tone", "control", "other"
    }
    if reason not in allowed:
        reason = "other"

    urgency = str(data.get("urgency") or "low").strip().lower()
    if urgency not in {"low", "medium", "high"}:
        urgency = "low"

    should = bool(data.get("should_intervene", False))
    if not tip:
        should = False

    out = {"should_intervene": should, "tip": tip, "reason_tag": reason, "urgency": urgency}
    # Optional: pass through extra fields if present (safe)
    if "tone_hint" in data:
        out["tone_hint"] = str(data.get("tone_hint") or "").strip()
    return out


def grade_exam(transcript: str) -> Dict[str, Any]:
    if client is None:
        return {
            "score": 0,
            "pass": False,
            "summary": "Missing OPENAI_API_KEY",
            "strengths": [],
            "improvements": ["Set OPENAI_API_KEY and restart the server."],
        }

    payload = (transcript or "")[-4500:].strip() or "(empty transcript)"
    r = client.responses.create(
        model=GRADER_MODEL,
        input=[
            {"role": "system", "content": GRADER_RUBRIC},
            {"role": "user", "content": payload},
        ],
        max_output_tokens=280,
    )

    txt = (r.output_text or "").strip()
    try:
        data = json.loads(txt)
    except Exception:
        data = {
            "score": 0,
            "pass": False,
            "summary": "Could not parse grader output.",
            "strengths": [],
            "improvements": ["Try again."],
        }

    score = int(data.get("score", 0) or 0)
    score = max(0, min(100, score))
    passed = bool(data.get("pass", score >= 70))
    strengths: List[str] = list(data.get("strengths") or [])
    improvements: List[str] = list(data.get("improvements") or [])

    return {
        "score": score,
        "pass": passed,
        "summary": str(data.get("summary") or "").strip(),
        "strengths": strengths[:5],
        "improvements": improvements[:7],
    }


def evaluate_checklist(transcript: str, customer_type: str = "", emotion_level: Optional[int] = None) -> Dict[str, Any]:
    """
    After-call evaluation focused on human skills + call script.
    Returns: checklist_score + itemized statuses + short improvements.
    """
    if client is None:
        return {
            "checklist_score": 0,
            "items": [],
            "highlights": [],
            "improvements": ["Set OPENAI_API_KEY and restart the server."],
            "next_time_say": [],
        }

    payload = (transcript or "")[-6500:].strip() or "(empty transcript)"
    meta = []
    if customer_type:
        meta.append(f"customer_type={customer_type}")
    if emotion_level is not None:
        meta.append(f"emotion_level={emotion_level}")
    meta_txt = ("\nMeta: " + ", ".join(meta)) if meta else ""

    r = client.responses.create(
        model=GRADER_MODEL,
        input=[
            {"role": "system", "content": CHECKLIST_SYSTEM_PROMPT},
            {"role": "user", "content": payload + meta_txt},
        ],
        max_output_tokens=520,
    )

    txt = (r.output_text or "").strip()
    try:
        data = json.loads(txt)
    except Exception:
        return {
            "checklist_score": 0,
            "items": [],
            "highlights": [],
            "improvements": ["Could not parse checklist output."],
            "next_time_say": [],
        }

    # Sanitize
    score = int(data.get("checklist_score", 0) or 0)
    score = max(0, min(100, score))

    items = data.get("items") or []
    clean_items = []
    for it in items:
        if not isinstance(it, dict):
            continue
        _id = str(it.get("id") or "").strip()[:40]
        title = str(it.get("title") or "").strip()[:60]
        status = str(it.get("status") or "missing").strip().lower()
        if status not in {"done", "partial", "missing"}:
            status = "missing"
        evidence = str(it.get("evidence") or "").strip()
        note = str(it.get("note") or "").strip()
        if evidence:
            evidence = " ".join(evidence.split()[:12])
        if note:
            note = " ".join(note.split()[:18])
        if _id and title:
            clean_items.append({"id": _id, "title": title, "status": status, "evidence": evidence, "note": note})

    highlights = [str(x).strip() for x in (data.get("highlights") or []) if str(x).strip()][:4]
    improvements = [str(x).strip() for x in (data.get("improvements") or []) if str(x).strip()][:6]
    next_time_say = [str(x).strip() for x in (data.get("next_time_say") or []) if str(x).strip()][:2]

    return {
        "checklist_score": score,
        "items": clean_items,
        "highlights": highlights,
        "improvements": improvements,
        "next_time_say": next_time_say,
    }
