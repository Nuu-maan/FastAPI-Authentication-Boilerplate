from datetime import datetime
from pydantic import BaseModel


class SessionOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None
    ip: str
    user_agent: str

    class Config:
        from_attributes = True
