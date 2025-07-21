from datetime import datetime

from pydantic import BaseModel


class ClickDetail(BaseModel):
    clicked_at: datetime
    user_agent: str | None = None

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    clicks_last_7_days: int
    clicks_last_30_days: int
    recent_clicks: list[ClickDetail]
