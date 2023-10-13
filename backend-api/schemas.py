from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint


class UserBase(BaseModel):
    email: EmailStr
    password: str
    fullname: str
    phone: str
    id_language: int
    # last_login: datetime
    # date_joined: datetime
    # status: bool = True
    # is_active: bool = False


class UserOut(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    phone: str
    id_language: int
    last_login: datetime
    date_joined: datetime

    # status: bool = True
    # is_active: bool = False

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
