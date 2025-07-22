import re
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.dependencies import get_current_user
from app.db.models import User
from app.db import dynamo as dynamo_db
from app.schemas.link import LinkCreate, LinkResponse, LinkListResponse
from app.services.shortener import generate_short_code

router = APIRouter()

CUSTOM_CODE_RE = re.compile(r"^[a-zA-Z0-9-]{3,20}$")


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(
    link_in: LinkCreate,
    current_user: User = Depends(get_current_user),
):
    original_url = str(link_in.original_url)
    if link_in.custom_code:
        if not CUSTOM_CODE_RE.match(link_in.custom_code):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="custom_code must be 3-20 chars, alphanumeric and hyphens only",
            )
        if dynamo_db.get_link(link_in.custom_code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom code already taken")
        short_code = link_in.custom_code
    else:
        for _ in range(5):
            short_code = generate_short_code()
            if not dynamo_db.get_link(short_code):
                break
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate unique code")

    ttl_days = link_in.expires_in_days if link_in.expires_in_days is not None else settings.DEFAULT_LINK_TTL_DAYS
    expires_at = None
    if ttl_days and ttl_days > 0:
        expires_at = int(time.time()) + ttl_days * 86400

    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    dynamo_db.put_link(
        short_code=short_code,
        original_url=original_url,
        user_id=str(current_user.id),
        created_at=created_at,
        expires_at=expires_at,
    )

    short_url = f"{settings.BASE_URL.rstrip('/')}/{short_code}"
    try:
        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except Exception:
        created_dt = datetime.utcnow()
    return LinkResponse(
        short_code=short_code,
        short_url=short_url,
        original_url=original_url,
        created_at=created_dt,
        expires_at=datetime.fromtimestamp(expires_at) if expires_at else None,
        click_count=0,
    )


@router.get("", response_model=LinkListResponse)
def list_links(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    user_id = str(current_user.id)
    items, _ = dynamo_db.query_links_by_user(user_id, limit=limit)
    total = dynamo_db.count_links_by_user(user_id)
    links = []
    for it in items:
        created_at = it.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.utcnow()
        expires_at_val = it.get("expires_at")
        expires_dt = datetime.fromtimestamp(expires_at_val) if expires_at_val else None
        links.append(
            LinkResponse(
                short_code=it["short_code"],
                short_url=f"{settings.BASE_URL.rstrip('/')}/{it['short_code']}",
                original_url=it["original_url"],
                created_at=dt,
                expires_at=expires_dt,
                click_count=it.get("click_count", 0),
            )
        )
    return LinkListResponse(links=links, total=total, page=page, limit=limit)


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    short_code: str,
    current_user: User = Depends(get_current_user),
):
    item = dynamo_db.get_link(short_code)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    if item.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this link")
    dynamo_db.delete_link(short_code)
