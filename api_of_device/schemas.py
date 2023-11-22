# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.types import conint


# 
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

    status: bool = True
    is_active: bool = False

    class Config:
        orm_mode = True
class UserCreate(UserBase):
    pass
class UserLogin(BaseModel):
    email: EmailStr
    password: str
# 
class DeviceListBase(BaseModel):
    id: int
    name: str
    rtu_bus_address: int
    tcp_gateway_ip: str
    tcp_gateway_port: int
class DeviceListOut(BaseModel):
    id: int
    name: str
    rtu_bus_address: int
    tcp_gateway_ip: str
    tcp_gateway_port: int

    class Config:
        orm_mode = True  
# 

# 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
