from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_code: str | None = None
    expires_in_days: int | None = None


class LinkResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None
    click_count: int

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    links: list[LinkResponse]
    total: int
    page: int
    limit: int
