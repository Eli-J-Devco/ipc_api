# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.types import conint

# from sqlalchemy import 


# <- User ->
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
# <- DeviceList ->
class DeviceListBase(BaseModel):
    id: int
    name: str
    rtu_bus_address: int
    tcp_gateway_ip: str
    tcp_gateway_port: int
class DeviceListOut(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None

    class Config:
        orm_mode = True  
# <- Communication ->
class CommunicationBase(BaseModel):
    name: Optional[str] = None
    namekey: Optional[str] = None
    id_driver_list: Optional[int] = None
    id_type_baud_rates: Optional[int] = None
    id_type_parity: Optional[int] = None
    id_type_stopbits: Optional[int] = None
    id_type_timeout: Optional[int] = None
    id_type_debug_level: Optional[int] = None
    # driver_list: DeviceListOut
    # note1: str
    # note1: str
    # status: bool = True
class RS485BaudRate(BaseModel):
    id: int = Field(..., alias='id')
    namekey: int = Field(...,examples=[9600],alias='baud')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485Parity(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='parity')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485StopBits(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='stop_bits')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485debuglevel(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='debuglevel')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485Timeout(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='timeout')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class ConfigRS485Base(BaseModel):
    baud:list[RS485BaudRate]
    parity:list[RS485Parity]
    stop_bits:list[RS485StopBits]
    debuglevel:list[RS485debuglevel]
    timeout:list[RS485Timeout]
    class Config:
        orm_mode = True
        
class CommunicationOut(CommunicationBase):
    id: int
    driver_list: DeviceListOut
    # driver_list: List[DeviceListOut]
    class Config():
        orm_mode = True
class CommunicationCreate(CommunicationBase):
    
    class Config:
        orm_mode = True 
# <- Config_information ->
class ConfigInformationBase(BaseModel):
    # id : int
    parent: Optional[int] = None
    name : Optional[str] = None
    namekey : Optional[str] = None
    description : Optional[str] = None
    value :Optional[int] = None
    type :Optional[int] = None
    id_type : Optional[int] = None
class ConfigInformationOut(ConfigInformationBase):
    id : Optional[int] = None
   
    class Config:
        orm_mode = True

# <- Ethernet ->
class EthernetBase(BaseModel):
    # id_project_setup: int
    name: Optional[str] = None
    namekey: Optional[str] = None
    id_type_ethernet: Optional[int] = None
    allow_dns: Optional[bool] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    mtu: Optional[str] = None
    dns1:  Optional[str] = None
    dns2:  Optional[str] = None
 
    # status: bool = True
class EthernetOut(EthernetBase):
    id: Optional[int] = None
    type_ethernet: ConfigInformationOut #Is it good ?
    class Config:
        orm_mode = True
class EthernetCreate(EthernetBase):
    class Config:
        orm_mode = True 
# 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None