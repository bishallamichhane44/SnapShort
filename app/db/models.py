import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    clicks = relationship("Click", back_populates="user")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_code = Column(String(20), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_hash = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)

    user = relationship("User", back_populates="clicks")
