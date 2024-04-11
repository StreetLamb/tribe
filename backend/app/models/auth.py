# Generic message
from sqlmodel import SQLModel


class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str