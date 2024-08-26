import uuid

from pydantic import BaseModel, EmailStr


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    user_name: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPair(BaseModel):
    access: str
    refresh: str
    token_type: str = "bearer"


class ChangePassword(TunedModel):
    old_password: str
    new_password: str