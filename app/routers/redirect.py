import hashlib
import time
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.db import dynamo as dynamo_db
from app.db import postgres as postgres_module
from app.services.analytics_service import record_click

router = APIRouter()


@router.get("/{short_code}", status_code=status.HTTP_301_MOVED_PERMANENTLY)
def redirect(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    item = dynamo_db.get_link(short_code)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")
    expires_at = item.get("expires_at")
    if expires_at and int(expires_at) < time.time():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This link has expired")

    dynamo_db.increment_click_count(short_code)
    original_url = item["original_url"]
    user_id = item.get("user_id")

    client_host = request.client.host if request.client else ""
    ip_hash = hashlib.sha256(client_host.encode()).hexdigest() if client_host else None
    user_agent = request.headers.get("user-agent")[:512] if request.headers.get("user-agent") else None

    def run_record():
        db = postgres_module.SessionLocal()
        try:
            record_click(db, short_code, UUID(user_id) if user_id else None, ip_hash, user_agent)
        finally:
            db.close()

    background_tasks.add_task(run_record)
    return RedirectResponse(url=original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)
