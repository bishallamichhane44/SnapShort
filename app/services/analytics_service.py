from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Click


def record_click(
    db: Session,
    short_code: str,
    user_id: UUID | None,
    ip_hash: str | None,
    user_agent: str | None,
) -> None:
    click = Click(
        short_code=short_code,
        user_id=user_id,
        ip_hash=ip_hash,
        user_agent=user_agent,
    )
    db.add(click)
    db.commit()


def get_click_counts(
    db: Session,
    short_code: str,
) -> tuple[int, int, int]:
    """Return (total, last_7_days, last_30_days)."""
    now = datetime.utcnow()
    day_7 = now - timedelta(days=7)
    day_30 = now - timedelta(days=30)

    total = db.query(func.count(Click.id)).filter(Click.short_code == short_code).scalar() or 0
    last_7 = db.query(func.count(Click.id)).filter(Click.short_code == short_code, Click.clicked_at >= day_7).scalar() or 0
    last_30 = db.query(func.count(Click.id)).filter(Click.short_code == short_code, Click.clicked_at >= day_30).scalar() or 0

    return total, last_7, last_30


def get_recent_clicks(db: Session, short_code: str, limit: int = 10) -> list[Click]:
    return (
        db.query(Click)
        .filter(Click.short_code == short_code)
        .order_by(Click.clicked_at.desc())
        .limit(limit)
        .all()
    )
