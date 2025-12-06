from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    is_active: bool = True
    role: str = "customer"


class User(UserBase):
    id: uuid.UUID
    oidc_oid: Optional[str]
    last_login_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    oidc_oid: Optional[str] = None
    password: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    oidc_oid: Optional[str] = None
    password: Optional[str] = None
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
