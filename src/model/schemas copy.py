# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import uuid
from datetime import datetime
from hashlib import sha256
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import (BaseModel, EmailStr, Field, computed_field,
                      root_validator, validator)
from pydantic.types import conint

# from pydantic_computed import Computed, computed


# from sqlalchemy import 
# <- driver_list ->
class DriverListBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    
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
    device_virtual: Optional[bool] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
    id_project_setup: Optional[int] = None
    id_device_type: Optional[int] = None
    id_communication: Optional[int] = None
    id_device_group: Optional[int] = None
    enable : Optional[bool] = None
    point : Optional[int] = None
    pv : Optional[int] = None
    model : Optional[int] = None
    function : Optional[int] = None
    
    point_p : Optional[int] = None #id
    
    value_p : Optional[float] = None
    send_p : Optional[bool] = None
    
    point_q : Optional[int] = None #id
    
    value_q : Optional[float] = None
    send_q : Optional[bool] = None
    
    point_pf : Optional[int] = None #id
    
    value_pf : Optional[float] = None
    send_pf : Optional[bool] = None
    max : Optional[float] = None
    allow_error : Optional[float] = None
    enable_poweroff : Optional[bool] = None
    inverter_shutdown : Optional[datetime] = None
    status : Optional[bool] = None

    class Config:
        orm_mode = True  
class DeviceState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
class DeviceCreate(BaseModel):
    # id: Optional[int] = None # Device number
    name: Optional[str] = None
    device_virtual: Optional[bool] = False
    # Modbus device connected
    id_communication: Optional[int] = Field(...,) 
    # driver_list_name:Optional[str] = None # table driver_list
    
    rtu_bus_address: Optional[int] = None
    tcp_gateway_port: Optional[int] = Field(...,examples=[502])
    tcp_gateway_ip: Optional[str] = None
    id_device_type: Optional[int] = None
    id_device_group: Optional[int] = None
    
    class Config:
        # allow_population_by_field_name = True
        # populate_by_name = True
        # from_attributes = True
        orm_mode = True
class MultipleDeviceCreate(BaseModel):
    # id: Optional[int] = None # Device number
    name: Optional[str]  = Field(...,description="") 
    device_virtual: Optional[bool] =  Field(...,examples=[False],description="") 
    # Modbus device connected
    id_communication: Optional[int] = Field(...,description="") 
    rtu_bus_address: Optional[int] = Field(...,) 
    tcp_gateway_port: Optional[int] = Field(...,examples=[502]) 
    tcp_gateway_ip: Optional[str] = Field(...,) 
    id_device_type: Optional[int] = Field(...,) 
    id_device_group: Optional[int] = Field(...,) 
    in_addcount: Optional[int] = Field(...,) 
    in_addmode: Optional[int] = Field()
    # 
    # in_addmode: Optional[int] = Field(Query(
    #     description="When adding, increment",
    # ))
    class Config:
        orm_mode = True
        # allow_population_by_field_name = True
        # populate_by_name = True
        # from_attributes = True
        # json_schema_extra
        # schema_extra  = {
        #     "example": {
        #         "name": "Mike",
                
        #     }
        # }
class DeviceDelete(BaseModel):
    id: Optional[int] =  Field(...)
    mode:Optional[int] =  Field(...,examples=[1],description="=1 Deactivate | =2 Delete")
    class Config:
        orm_mode = True
class DeviceUpdateBase(BaseModel):
    id: Optional[int] = None # Device number
    name: Optional[str] = None
    
    rtu_bus_address: Optional[int] = None
    tcp_gateway_port: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    id_device_type: Optional[int] = None
    id_device_group: Optional[int] = None
    class Config:
        # allow_population_by_field_name = True
        # populate_by_name = True
        # from_attributes = True
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
    id: int
    driver_list: DriverListBase
    class Config:
        orm_mode = True 
class RS485State(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True

# <- device_type ->
class DeviceTypeBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    class Config:
        orm_mode = True
# <- template_library ->
class TemplateBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    
    class Config:
        orm_mode = True

class Point_RegisterBase(BaseModel):
    
    class Config:
        orm_mode = True
# <- device_group ->
class DeviceGroupBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    id_template: Optional[int] = None
    templates_library: TemplateBase
    class Config:
        orm_mode = True

# <- DeviceConfig ->
class DeviceConfigOut(BaseModel):
    device_list:list[DeviceListBase]
    device_type:list[DeviceTypeBase]
    device_group:list[DeviceGroupBase]
    communication:list[CommunicationCreate]
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
# <- project ->
class PageBase(BaseModel):
    id : Optional[int] = None
    name : Optional[str] = None
    description : Optional[str] = None
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):

    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None
    
    id_first_page_on_login: Optional[int] = None
    id_logging_interval: Optional[int] = None
    id_scheduled_upload_time: Optional[int] = None
    number_times_retry: Optional[int] = None
    id_time_wait_before_retry: Optional[int] = None
    id_upload_debug_information: Optional[int] = None
    enable_upload_data_on_alarm_status: Optional[bool] = None
    enable_upload_data_on_low_disk: Optional[bool] = None
    enable_upload_data_on_system_startup: Optional[bool] = None
    
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None
    
    id_time_zone : Optional[int] = None
    Time1cycle : Optional[float] = None
    sampling_time1cycle : Optional[float] = None

    enable_zero_export : Optional[bool] = None
    value_zero_export : Optional[float] = None

    enable_limit_energy : Optional[bool] = None
    value_limit_energy : Optional[float] = None
    
    modhopper1 : Optional[int] = None
    modhopper2 : Optional[int] = None
    modhopper_key : Optional[str] = None
    modhopper_rf_config : Optional[int] = None
    modhopper_rf_channel : Optional[int] = None
    status : Optional[bool] = None
    logging_interval:type_logging_interval
    logging_interval_list:list[type_logging_interval]
    first_page_on_login:PageBase
    first_page_on_login_list:list[PageBase]
    class Config:
        orm_mode = True
class ProjectOut(ProjectBase):
    id: Optional[int] = None
   
    class Config:
        orm_mode = True
class ProjectCreate(ProjectBase):
    pass
class ProjectUpdate(ProjectBase):
    pass

class ProjectRemoteAccessUpdate(BaseModel):
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None
    class Config:
        orm_mode = True
class ProjectLoggingRateUpdate(BaseModel):
    id_logging_interval: Optional[int] = None
    class Config:
        orm_mode = True
class ProjectPageLoginUpdate(BaseModel):
    id_first_page_on_login: Optional[int] = None
    class Config:
        orm_mode = True
class ProjectSearchModBusUpdate(BaseModel):
    # enable_search_modbus_rtu_device: Optional[int] = None
    enable_search_modbus_rtu_device: bool = Field(..., alias='search_modbus_rtu_device')
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class ProjectState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True
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


# <- device_point_list ->


class TypeUnitsBase(BaseModel):
    id: Optional[int] = Field(..., nullable=True, alias='id')
    namekey: Optional[str] = Field(..., nullable=True,alias='Units')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class DataTypeBase(BaseModel):

    id: Optional[int] = Field(..., alias='id')
    namekey: Optional[str] = Field(...,alias='Data Type')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class TypeByteOrderBase(BaseModel):
    id: Optional[int] = Field(..., alias='id')
    namekey: Optional[str]  = Field(...,alias='Byte Order')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class TypePointBase(BaseModel):
    id: Optional[int] = Field(..., alias='id')
    namekey: Optional[str] = Field(...,alias='Type Point')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class TypeClassBase(BaseModel):
    id:  Optional[int] = Field(..., alias='id')
    namekey:  Optional[str] = Field(...,alias='TypeClass')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class PointBase(BaseModel):
    id : Optional[int] = None
    id_pointkey : Optional[int] = None
    # --------------------------------------------------
    id_template : Optional[int] = None
    # 
    name : Optional[str] = None
    nameedit : Optional[bool] = None
    id_type_units : Optional[int] = None
    unitsedit : Optional[bool] = None
    equation : Optional[int] = None
    config : Optional[int] = None
    register : Optional[int] = None
    id_type_datatype : Optional[int] = None
    id_type_byteorder : Optional[int] = None
    slope : Optional[float] = None
    slopeenabled : Optional[int] = None
    offset : Optional[float] = None
    offsetenabled : Optional[bool] = None
    multreg : Optional[int] = None
    multregenabled : Optional[bool] = None
    userscaleenabled : Optional[bool] = None
    invalidvalue : Optional[int] = None
    invalidvalueenabled : Optional[bool] = None
    extendednumpoints : Optional[int] = None
    extendedregblocks : Optional[int] = None
    status : Optional[bool] = None
    function : Optional[str] = None
    constants : Optional[float] = None
    class Config:
        orm_mode = True
class PointOutBase(PointBase):
    # 
    type_units  : Optional[TypeUnitsBase] = None
    type_datatype  : Optional[DataTypeBase] = None 
    type_byteorder  : Optional[TypeByteOrderBase] = None
    
    type_point  : Optional[TypePointBase] = None 
    type_class  : Optional[TypeClassBase] = None 
    class Config:
        orm_mode = True
class PointUpdateBase(PointBase):
    # id : Optional[int] = None
    equation : Optional[int] = Field(...,examples=[1] ,nullable=False)
    # id_pointkey : Optional[int] = None
    # id_template : Optional[int] = None
    class Config:
        orm_mode = True
        # fields = {'id_pointkey': {'exclude': True}}

class DevicePointListBase(BaseModel):
    id : Optional[int] = None
    id_pointkey : Optional[int] = None
    # --------------------------------------------------
    id_template : Optional[int] = None
    id_device_group : Optional[int] = None
    id_device_list : Optional[int] = None
    id_point_list : Optional[int] = None
    # -------------------------------------------------- 
    class Config:
        orm_mode = True
        from_attributes = True
class PointInfoTemplateBase(BaseModel):
    id_point: Optional[int]=None
    # id_template: Optional[int]=None
class PointChangeNumberBase(BaseModel):
    id_template: Optional[int]=None
    number_point: Optional[int]=Field(None, ge=1)
class PointDeleteTemplateBase(BaseModel):
    id_template: Optional[int]=None
    id_point:Optional[list[int]]=None
    
    class Config:
        orm_mode = True
        from_attributes = True
class PointTemplateOutBase(PointOutBase):
    type_units_list: Optional[list[TypeUnitsBase]] = None
    type_datatype_list: Optional[list[DataTypeBase]] = None
    type_byteorder_list: Optional[list[TypeByteOrderBase]] = None
    
    type_point_list: Optional[list[TypePointBase]] = None
    type_class_list: Optional[list[TypeClassBase]] = None
    class Config:
        orm_mode = True

# <- register_list -> 
class TypeFunctionBase(BaseModel):
    id: Optional[int] = Field(..., nullable=True, alias='id')
    namekey: Optional[str] = Field(..., nullable=True,alias='Function')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RegisterBase(BaseModel):
    # --------------------------------------------------
    id_template : Optional[int] = None
    addr : Optional[int] = None
    count : Optional[int] = None
    id_type_function : Optional[int] = None
    status : Optional[bool] = None
    class Config:
        orm_mode = True
class RegisterCreateBase(RegisterBase):
    pass
    class Config:
        orm_mode = True
class RegisterOutBase(RegisterBase):
    id : Optional[int] = None
    class Config:
        orm_mode = True

class RegisterConfigOutBase(BaseModel):
    
    register_list: Optional[list[RegisterOutBase]] = None
    type_function:Optional[list[TypeFunctionBase]] = None 
    class Config:
        orm_mode = True
class RegisterListBase(RegisterBase):
    id : Optional[int] = None
    # --------------------------------------------------
    type_function: Optional[TypeFunctionBase] = None 
    class Config:
        orm_mode = True

# <-  -> 

class TemplateCreateBase(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None
    id_template_type:Optional[int] = None
    class Config:
        orm_mode = True
class TemplateOutBase(TemplateCreateBase):
    id: Optional[int] = None
    # name: Optional[str] = None
    # status: Optional[bool] = None
    # point_list : list[PointOutBase]
    class Config:
        orm_mode = True
class TemplateUpdateBase(TemplateCreateBase):
    id: Optional[int] = None
    class Config:
        orm_mode = True        
class TemplateTypeBase(BaseModel):
    id: Optional[int] = Field(..., alias='id')
    namekey: Optional[str] = Field(..., alias='types')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True

    # id: Optional[int] = None
    # class Config:
    #     orm_mode = True        
class TemplateDelete(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
# <-  -> 
class PointDataType(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(...,alias='Data Type')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class PointByteOrder(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(...,alias='Byte Order')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class PointUnit(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(...,alias='Unit')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True

# <-  -> 
class DeviceGroupCreateBase(BaseModel):
    name: Optional[str] = None
    # status: Optional[bool] = None
    id_template: Optional[int] = None
    class Config:
        orm_mode = True
class DeviceGroupBase(DeviceGroupCreateBase):
    id: Optional[int] = None 
    # name: Optional[str] = None
    # status: Optional[bool] = None
    # id_template: Optional[int] = None
    # templates_library: TemplateOutBase
    
    class Config:
        validate_assignment = True
    # @validator("id", pre=True, always=True)
    # def _encryption_id(cls, id: str):
    #     id_hash=str(id)
    #     return sha256(id_hash.encode('utf-8')).hexdigest()
class DeviceGroupStateBase(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
class DeviceGroupOutBase(BaseModel):
    id: Optional[int] = None 
    name: Optional[str] = None
    status: Optional[bool] = None
    id_template: Optional[int] = None
    # templates_library: TemplateOutBase
    template_list:Optional[list[TemplateBase]] = None 
    class Config:
        orm_mode = True
class TemplateGroupDeviceOutBase(BaseModel):
    device_group:DeviceGroupBase=None
    data_type:list[PointDataType]=None
    byte_order:list[PointByteOrder]=None
    point_unit:list[PointUnit]=None
    point_list : list[PointOutBase]=None
    register_list : list[RegisterListBase]=None
    
    class Config:
        orm_mode = True

# <-  -> 
class DeviceListOfPointListOut(DeviceListOut):
    point_p_list:Optional[PointBase] = None
    point_q_list:Optional[PointBase] = None
    point_pf_list:Optional[PointBase] = None
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
# <-  ->
class TemplateListBase(BaseModel):
    data_type:list[PointDataType]=None
    byte_order:list[PointByteOrder]=None
    point_unit:list[PointUnit]=None
    point_list : list[PointOutBase]=None
    register_list : list[RegisterListBase]=None
    
    class Config:
        orm_mode = True
# <-  -> 
# <-  -> 
# class Token(BaseModel):
#     class TokenRole(RoleOut):
#         screen: Optional[list[ScreenOut]]= None
#         class Config:
#             orm_mode = True
#     refresh_token: str
#     access_token: str
#     token_type: str
#     user: Optional[UserLoginOut] = None
#     screen: list[ScreenBase]
#     role:list[TokenRole]
# class TokenData(BaseModel):
#     id: Optional[str] = None
# class TokenItem(BaseModel):
#     refresh_token: Optional[str] = None
