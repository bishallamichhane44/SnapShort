from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db.models import User
from app.db import dynamo as dynamo_db
from app.db.postgres import get_db
from app.schemas.analytics import AnalyticsResponse, ClickDetail
from app.services.analytics_service import get_click_counts, get_recent_clicks

router = APIRouter()


@router.get("/{short_code}", response_model=AnalyticsResponse)
def get_analytics(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = dynamo_db.get_link(short_code)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    if item.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this link")

    total_clicks = item.get("click_count", 0)
    _, clicks_7, clicks_30 = get_click_counts(db, short_code)
    recent = get_recent_clicks(db, short_code, limit=10)

    return AnalyticsResponse(
        short_code=short_code,
        original_url=item["original_url"],
        total_clicks=total_clicks,
        clicks_last_7_days=clicks_7,
        clicks_last_30_days=clicks_30,
        recent_clicks=[ClickDetail(clicked_at=c.clicked_at, user_agent=c.user_agent) for c in recent],
    )
