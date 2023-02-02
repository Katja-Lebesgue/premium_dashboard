from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str


class TokenIn(BaseModel):
    token: str


class CodeIn(BaseModel):
    code: str
