# auth.py
from typing import Optional
import os
from fastapi import Request
from fastapi.responses import RedirectResponse

from settings import USERS


def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("user"))


def is_admin(email: str) -> bool:
    admins = os.getenv("ADMIN_EMAILS", "")
    admin_set = {x.strip().lower() for x in admins.split(",") if x.strip()}
    return (email or "").strip().lower() in admin_set


def require_login(request: Request) -> Optional[RedirectResponse]:
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    return None


def check_credentials(email: str, password: str) -> bool:
    email = (email or "").strip().lower()
    password = (password or "").strip()
    if not email or not password:
        return False
    if USERS:
        return USERS.get(email) == password
    return True  # MVP local-only
