from fastapi import Header, HTTPException, Request

from app.config import settings


def verify_api_key(x_api_key: str = Header(default=None)):
    if not settings.API_KEY:
        raise HTTPException(500, "Server misconfigured: API key not set.")
    if x_api_key != settings.API_KEY:
        raise HTTPException(401, "Invalid or missing API key.")


def verify_host(request: Request):
    if not settings.ALLOWED_HOSTS:
        return
    host = request.headers.get("host", "").split(":")[0]
    if host not in settings.ALLOWED_HOSTS:
        raise HTTPException(403, f"Host '{host}' not allowed.")
