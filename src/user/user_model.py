# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
from typing import Optional

from pydantic import BaseModel

from ..role.role_model import RoleBase


class User(BaseModel):
    id: Optional[int] = None

class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status: bool = True


class UserCreate(UserBase):
    email: str
    password: str
    role: list[RoleBase]


class UserUpdate(UserBase):
    id: int
    role: Optional[list[RoleBase]]


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class UserList(UserBase):
    id: int
    email: str
    role: list[RoleBase]


class UserFull(UserBase):
    id: Optional[int] = None
    salt: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    create_date: Optional[datetime.datetime] = None
    updated_date: Optional[datetime.datetime] = None
    last_login: Optional[datetime.datetime] = None
    create_by: Optional[str] = None
    updated_by: Optional[str] = None


