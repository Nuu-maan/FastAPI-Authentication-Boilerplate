from pydantic import BaseModel


class MessageOut(BaseModel):
    message: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
