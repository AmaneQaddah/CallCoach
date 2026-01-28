import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from settings import APP_SECRET, HAS_KEY, OpenAI, ONBOARDING
from auth import is_logged_in, require_login, check_credentials, is_admin
from pages import (
    build_login_html,
    build_dashboard_html,
    build_training_picker_html,
    build_training_live_html,
    build_exam_html,
    build_admin_html,
    build_training_report_html,
    build_exam_report_html,
    build_onboarding_html,
)
from prompts import build_customer_instructions
from evaluation import coach_tips, grade_exam, evaluate_checklist
from openai_realtime import webrtc_answer_sdp
from storage import save_attempt, list_attempts, get_attempt

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET, same_site="lax", https_only=False)

# -------------------------
# Static
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)  # avoids crash if folder missing
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


# -------------------------
# Helpers / guards
# -------------------------
def require_openai_key_json():
    if not HAS_KEY:
        return JSONResponse(
            {"detail": "Missing OPENAI_API_KEY (.env). Set it and restart. See /setup"},
            status_code=500
        )
    if OpenAI is None:
        return JSONResponse(
            {"detail": "Missing openai python package. Run: pip install openai"},
            status_code=500
        )
    return None


def require_admin(request: Request):
    user = (request.session.get("user") or "").strip().lower()
    if not user or not is_admin(user):
        return JSONResponse({"detail": "Admin only"}, status_code=403)
    return None


def _me(request: Request) -> str:
    return (request.session.get("user") or "").strip().lower()


def _role(request: Request) -> str:
    return (request.session.get("role") or "trainee").strip().lower()


def _can_view_attempt(request: Request, attempt: dict) -> bool:
    me = _me(request)
    if not me:
        return False
    if is_admin(me):
        return True
    return (attempt.get("user_email") or "").strip().lower() == me


def _ensure_attempt_id(maybe_id):
    if isinstance(maybe_id, int) and maybe_id > 0:
        return maybe_id
    try:
        items = list_attempts(limit=1)
        if items and isinstance(items[0].get("id"), int):
            return int(items[0]["id"])
    except Exception:
        pass
    return None


def _onboarding_done(request: Request) -> bool:
    return bool(request.session.get("onboarding_done"))


def _require_onboarding_or_redirect(request: Request):
    if not _onboarding_done(request):
        return RedirectResponse(url="/onboarding", status_code=302)
    return None


# -------------------------
# Routes
# -------------------------
@app.get("/")
def root(request: Request):
    if is_logged_in(request):
        user = _me(request)
        role = _role(request)
        if role == "recruiter" and is_admin(user):
            return RedirectResponse(url="/admin", status_code=302)
        return RedirectResponse(url="/app", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/setup", response_class=HTMLResponse)
def setup_page():
    msg = "OPENAI_API_KEY is missing" if not HAS_KEY else "openai package is missing"
    return HTMLResponse(f"""
<!doctype html>
<html><head><meta charset="utf-8"><title>Setup</title></head>
<body style="font-family:Arial;padding:24px;max-width:900px">
  <h2>Setup</h2>
  <p><b>{msg}</b></p>
  <pre style="background:#f5f5f5;padding:12px;border-radius:8px">
Create .env (same folder as app.py):
OPENAI_API_KEY=sk-...
APP_SECRET=change-me
ADMIN_EMAILS=recruiter@company.com

Run:
uvicorn app:app --host 127.0.0.1 --port 8040 --reload
  </pre>
</body></html>
""")


# -------------------------
# Auth
# -------------------------
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    if is_logged_in(request):
        user = _me(request)
        role = _role(request)
        if role == "recruiter" and is_admin(user):
            return RedirectResponse(url="/admin", status_code=302)
        return RedirectResponse(url="/app", status_code=302)
    return HTMLResponse(build_login_html())


@app.post("/login")
async def login_post(request: Request):
    data = await request.json()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    role = (data.get("role") or "trainee").strip().lower()
    role = "recruiter" if role == "recruiter" else "trainee"

    if not check_credentials(email, password):
        return JSONResponse({"detail": "Invalid email or password"}, status_code=401)

    if role == "recruiter" and not is_admin(email):
        return JSONResponse({"detail": "Not authorized for Recruiter view."}, status_code=403)

    request.session["user"] = email
    request.session["role"] = role

    redirect = "/admin" if role == "recruiter" else "/app"
    return JSONResponse({"ok": True, "redirect": redirect})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# -------------------------
# Dashboard
# -------------------------
@app.get("/app", response_class=HTMLResponse)
def app_dashboard(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect

    if _role(request) == "recruiter":
        return RedirectResponse(url="/admin", status_code=302)

    user = _me(request)
    training_enabled = _onboarding_done(request)
    return HTMLResponse(build_dashboard_html(user, show_admin=False, training_enabled=training_enabled))


# -------------------------
# Onboarding (separate path)
# -------------------------
@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_page(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect

    if _role(request) == "recruiter":
        return RedirectResponse(url="/admin", status_code=302)

    return HTMLResponse(build_onboarding_html(ONBOARDING, done=_onboarding_done(request)))


@app.post("/onboarding/done")
def onboarding_done(request: Request):
    redirect = require_login(request)
    if redirect:
        return JSONResponse({"detail": "Not logged in"}, status_code=401)

    if _role(request) == "recruiter":
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    request.session["onboarding_done"] = True
    return JSONResponse({"ok": True})


# -------------------------
# Training (LOCKED until onboarding done)
# -------------------------
@app.get("/training", response_class=HTMLResponse)
def training_picker(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    if _role(request) == "recruiter":
        return RedirectResponse(url="/admin", status_code=302)

    gate = _require_onboarding_or_redirect(request)
    if gate:
        return gate

    return HTMLResponse(build_training_picker_html())


@app.get("/training/live", response_class=HTMLResponse)
def training_live(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    if _role(request) == "recruiter":
        return RedirectResponse(url="/admin", status_code=302)

    gate = _require_onboarding_or_redirect(request)
    if gate:
        return gate

    return HTMLResponse(build_training_live_html())


@app.get("/training/report/{attempt_id}", response_class=HTMLResponse)
def training_report(request: Request, attempt_id: int):
    redirect = require_login(request)
    if redirect:
        return redirect

    a = get_attempt(attempt_id)
    if not a:
        return HTMLResponse("Not found", status_code=404)
    if not _can_view_attempt(request, a):
        return HTMLResponse("Forbidden", status_code=403)
    if (a.get("mode") or "") != "training":
        return HTMLResponse("Not a training attempt", status_code=400)

    return HTMLResponse(build_training_report_html(a))


# -------------------------
# Exam (VOICE)  ✅✅✅
# -------------------------
@app.get("/exam", response_class=HTMLResponse)
def exam_page(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    if _role(request) == "recruiter":
        return RedirectResponse(url="/admin", status_code=302)
    return HTMLResponse(build_exam_html())


@app.get("/exam/report/{attempt_id}", response_class=HTMLResponse)
def exam_report(request: Request, attempt_id: int):
    redirect = require_login(request)
    if redirect:
        return redirect

    a = get_attempt(attempt_id)
    if not a:
        return HTMLResponse("Not found", status_code=404)
    if not _can_view_attempt(request, a):
        return HTMLResponse("Forbidden", status_code=403)
    if (a.get("mode") or "") != "exam":
        return HTMLResponse("Not an exam attempt", status_code=400)

    return HTMLResponse(build_exam_report_html(a))


# -------------------------
# Realtime session (WebRTC)
# Used by BOTH training + exam
# -------------------------
@app.post("/session")
async def session_endpoint(request: Request):
    redirect = require_login(request)
    if redirect:
        return JSONResponse({"detail": "Not logged in"}, status_code=401)

    if not HAS_KEY:
        return JSONResponse({"detail": "Missing OPENAI_API_KEY. See /setup"}, status_code=500)

    offer_sdp = (await request.body()).decode("utf-8", errors="ignore")
    if not offer_sdp:
        return JSONResponse({"detail": "Empty SDP offer"}, status_code=400)

    level = (request.query_params.get("level") or "easy").strip().lower()
    scenario_id = (request.query_params.get("scenario_id") or "").strip()

    instructions = build_customer_instructions(level, scenario_id=scenario_id)

    try:
        answer_sdp = webrtc_answer_sdp(offer_sdp, instructions)
        return PlainTextResponse(answer_sdp, media_type="application/sdp")
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


# -------------------------
# Live coach (Training only)
# -------------------------
@app.post("/coach")
async def coach_endpoint(request: Request):
    redirect = require_login(request)
    if redirect:
        return JSONResponse({"detail": "Not logged in"}, status_code=401)

    guard = require_openai_key_json()
    if guard:
        return guard

    data = await request.json()
    transcript = (data.get("transcript") or "").strip()

    try:
        return JSONResponse(coach_tips(transcript))
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


# -------------------------
# Training after-call -> returns attempt_id for redirect
# -------------------------
@app.post("/aftercall")
async def aftercall_endpoint(request: Request):
    redirect = require_login(request)
    if redirect:
        return JSONResponse({"detail": "Not logged in"}, status_code=401)

    data = await request.json()
    transcript = (data.get("transcript") or "").strip()
    level = (data.get("level") or "easy").strip().lower()
    user_email = _me(request)

    if not HAS_KEY or OpenAI is None:
        maybe_id = save_attempt({
            "user_email": user_email,
            "mode": "training",
            "level": level,
            "transcript": transcript,
        })
        attempt_id = _ensure_attempt_id(maybe_id)
        return JSONResponse({"ok": True, "attempt_id": attempt_id})

    report = evaluate_checklist(transcript)

    maybe_id = save_attempt({
        "user_email": user_email,
        "mode": "training",
        "level": level,
        "transcript": transcript,
        "checklist_score": int(report.get("checklist_score", 0) or 0),
        "checklist_json": json.dumps(report, ensure_ascii=False),
    })
    attempt_id = _ensure_attempt_id(maybe_id)
    return JSONResponse({"ok": True, "attempt_id": attempt_id})


# -------------------------
# Exam grading -> returns attempt_id for redirect
# -------------------------
@app.post("/grade")
async def grade_endpoint(request: Request):
    redirect = require_login(request)
    if redirect:
        return JSONResponse({"detail": "Not logged in"}, status_code=401)

    guard = require_openai_key_json()
    if guard:
        return guard

    data = await request.json()
    transcript = (data.get("transcript") or "").strip()
    level = (data.get("level") or request.query_params.get("level") or "easy").strip().lower()
    user_email = _me(request)

    result = grade_exam(transcript)
    checklist = evaluate_checklist(transcript)

    maybe_id = save_attempt({
        "user_email": user_email,
        "mode": "exam",
        "level": level,
        "transcript": transcript,
        "score": int(result.get("score", 0) or 0),
        "passed": 1 if result.get("pass") else 0,
        "summary": result.get("summary", ""),
        "strengths": json.dumps(result.get("strengths", []), ensure_ascii=False),
        "improvements": json.dumps(result.get("improvements", []), ensure_ascii=False),
        "checklist_score": int(checklist.get("checklist_score", 0) or 0),
        "checklist_json": json.dumps(checklist, ensure_ascii=False),
    })
    attempt_id = _ensure_attempt_id(maybe_id)
    return JSONResponse({"ok": True, "attempt_id": attempt_id})


# -------------------------
# Admin
# -------------------------
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    guard = require_admin(request)
    if guard:
        return HTMLResponse("Admin only", status_code=403)
    return HTMLResponse(build_admin_html(request.session.get("user", "")))


@app.get("/admin/api/attempts")
def admin_attempts(request: Request):
    guard = require_admin(request)
    if guard:
        return guard
    return JSONResponse({"items": list_attempts(limit=300)})


@app.get("/admin/api/attempt/{attempt_id}")
def admin_attempt(request: Request, attempt_id: int):
    guard = require_admin(request)
    if guard:
        return guard
    a = get_attempt(attempt_id)
    if not a:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(a)
