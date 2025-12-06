from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, func, Uuid, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.uuid_generate_v4()
    )
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    oidc_oid: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    role: Mapped[str] = mapped_column(String, default="customer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
