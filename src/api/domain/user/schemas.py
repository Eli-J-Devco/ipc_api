# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import uuid
from datetime import datetime
from hashlib import sha256
from typing import List, Optional

# 
from fastapi import APIRouter, Depends, Query
from pydantic import (BaseModel, EmailStr, Field, computed_field,
                      root_validator, validator)
from pydantic.types import conint

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
# from model.schemas import RoleOut, ScreenBase, ScreenOut, UserLoginOut


# <- User ->
class ScreenBase(BaseModel):
    # id: Optional[int] = None 
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None
    
    class Config:
        orm_mode = True
class ScreenOut(ScreenBase):
    id: Optional[int] = None 
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None
    auth: Optional[int] = None 
    class Config:
        orm_mode = True         
class RoleBase(BaseModel):
    # id: Optional[int] = None 
    name: Optional[str] = None
    description: Optional[str] = None
    # status: Optional[bool] = None
    class Config:
        orm_mode = True
class RoleOut(RoleBase):
    id: Optional[int] = None
    class Config:
        orm_mode = True
class RoleCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    class Config:
        orm_mode = True
class RoleUpdate(RoleBase):
    id: Optional[int] = None 
    class Config:
        orm_mode = True
class RoleScreenUpdate(BaseModel):
    class RoleScreen(BaseModel):
        id_screen:Optional[int] = None
        auth:Optional[int] = None
    id_role:Optional[int] = None
    role_screen:list[RoleScreen]=None
    class Config:
        orm_mode = True
class RoleScreenOut(BaseModel):
    id_role:Optional[int] = None
    id_screen:Optional[int] = None
    auth:Optional[int] = None
    name_screen: Optional[str] = None
    class Config:
        orm_mode = True
class RoleScreenState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
class UserBase(BaseModel):
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    email: Optional[EmailStr] = None 
    phone: Optional[str] = None
    # id_language: Optional[int] = Field(...,examples=[1])
    # 
    email:Optional[str] = None
    password:Optional[str] = None
    # salt:Optional[str] = None
    phone:Optional[str] = None
    
    # status:Optional[bool] = None
    # fullname: str
    # create_date:Optional[datetime] = None
    # last_login:Optional[datetime] = None
    
    # create_by:Optional[str] = None
    # updated_date:Optional[datetime] = None
    # updated_by:Optional[str] = None
    
    
    # last_login: datetime
    # date_joined: datetime
    # status: bool = True
    # is_active: bool = False
class UserOut(BaseModel):
    id: int
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    email :Optional[EmailStr] = None 
    
    phone:Optional[str] = None
    # fullname: str
    # id_language: int
    # last_login: datetime
    # date_joined: datetime

    status: bool = True
    # is_active: bool = False

    class Config:
        orm_mode = True
class UserLoginOut(BaseModel):
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    # fullname: str
    phone: str
    # id_language: int
    # last_login: datetime
    # date_joined: datetime

    # status: bool = True
    # is_active: bool = False
    auth: Optional[int] = None

    class Config:
        orm_mode = True
class UserUpdate(BaseModel):
    class Role(BaseModel):
        id: Optional[int] = None
        class Config:
            orm_mode = True
    id:Optional[int] = None
    email: EmailStr
    # fullname: Optional[str] = None
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    phone: Optional[str] = None
    # id_language: Optional[int] = None
    
    role: list[Role]
    class Config:
        orm_mode = True
class UserChangePassword(BaseModel):
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    class Config:
        orm_mode = True
class UserResetPassword(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    password: Optional[str] = None
class UserRoleCreate(UserBase):
    class Role(BaseModel):
        id: Optional[int] = None
        class Config:
            orm_mode = True
    role: list[Role]
    class Config:
        orm_mode = True
class UserRoleOut(UserOut):
    role: list[RoleOut]
    class Config:
        orm_mode = True
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class UserActive(BaseModel):
    id: Optional[int] = None
    active: Optional[bool] = None
class UserStateOut(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
# 
class Token(BaseModel):
    class TokenRole(RoleOut):
        screen: Optional[list[ScreenOut]]= None
        class Config:
            orm_mode = True
    refresh_token: str = None
    access_token: str = None
    token_type: str = None
    user: Optional[UserLoginOut] = None
    # screen: list[ScreenBase]=[]
    # role:list[TokenRole] = None
    permissions: list=None
class TokenData(BaseModel):
    id: Optional[str] = None

class TokenItem(BaseModel):
    refresh_token: Optional[str] = None