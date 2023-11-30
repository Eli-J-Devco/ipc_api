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
    id: Optional[int] = None
    name: Optional[str] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
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
class RS485ConfigBase(BaseModel):
    baud:list[RS485BaudRate]
    parity:list[RS485Parity]
    stop_bits:list[RS485StopBits]
    debuglevel:list[RS485debuglevel]
    timeout:list[RS485Timeout]
    class Config:
        orm_mode = True
class SerialBase(BaseModel):
    serial_port:Optional[str] = None
    class Config:
        orm_mode = True
class SerialListBase(BaseModel):
    serial_list:list[SerialBase]
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
class RS485State(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
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
class NetworkInterfaceBase(BaseModel):
    interface: Optional[str] = None
    information: list[str] = None
    class Config:
        orm_mode = True
class NetworkBase(BaseModel):
    network:list[NetworkInterfaceBase]
    class Config:
        orm_mode = True
# <- site_information ->
class SiteInformBase(BaseModel):
    # id_project_setup: int
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None
   
class SiteInformOut(SiteInformBase):
    id: Optional[int] = None
   
    class Config:
        orm_mode = True
class SiteInformCreate(SiteInformBase):
    class Config:
        orm_mode = True
class SiteInformUpdate(SiteInformBase):
    class Config:
        orm_mode = True 
# <- upload_channel ->
class type_protocol(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='Protocol')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class type_logging_interval(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='Logging_Interval')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class UploadChannelBase(BaseModel):
    # id_project_setup: int
    name: Optional[str] = None
    id_type_protocol: Optional[int] = None
    uploadurl: Optional[str] = None
    password: Optional[str] = None
    selected_upload: Optional[str] = None
    id_type_logging_interval: Optional[int] = None
    enable: Optional[bool] = None
    allow_remote_configuration: Optional[bool] = None
    class Config:
        orm_mode = True 
class UploadChannelOut(UploadChannelBase):
    id: Optional[int] = None
    type_protocol: type_protocol
    type_logging_interval: type_logging_interval
    status: Optional[bool] = None
    class Config:
        orm_mode = True
class AllUploadChannelOut(BaseModel):
    all_channel: list[UploadChannelOut]
   
    class Config:
        orm_mode = True

class UploadChannelCreate(UploadChannelBase):
    class Config:
        orm_mode = True 
class UploadChannelConfig(BaseModel):
    device_list: list[DeviceListBase]
    type_protocol:list[type_protocol]
    type_logging_interval:list[type_logging_interval]
    class Config:
        orm_mode = True
# 
class UploadChannelUpdate(UploadChannelBase):
    # del UploadChannelBase.status 
    # id: int
    id: Optional[int] = None
    class Config:
        orm_mode = True 
class UploadChannelState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True
# 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
