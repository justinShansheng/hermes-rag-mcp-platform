from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth_utils import decode_token
from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(request: Request, creds: Optional[HTTPAuthorizationCredentials] = None):
    token = settings.api_key
    if not token:
        return None

    auth_header = request.headers.get("authorization") or ""
    if auth_header.startswith("Bearer "):
        provided = auth_header.split(" ", 1)[1].strip()
        try:
            return decode_token(provided)
        except HTTPException:
            pass

    if creds and creds.credentials == token:
        return "demo-user"

    raise HTTPException(status_code=401, detail="Invalid or missing API token")
