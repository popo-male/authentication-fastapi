from datetime import datetime
import uuid
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: uuid.UUID
    email: str
    role: str
    exp: datetime
    iat: datetime

class TokenData(BaseModel):
    username: str | None = None