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
from api.domain.deviceGroup.schemas import DeviceGroupBase
from api.domain.template.schemas import TemplateBase
# import api.domain.deviceGroup.schemas as deviceGroup_schemas
# from model.schemas import (PointBase, PointByteOrder, PointDataType,
#                            PointOutBase, PointUnit, RegisterListBase)
from model.schemas import DeviceTypeBase, DriverListBase, PointBase


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
class CommunicationCreate(CommunicationBase):
    id: int
    driver_list: DriverListBase
    
    class Config:
        orm_mode = True
# class DeviceTypeBase(BaseModel):
#     id: Optional[int] = None
#     name: Optional[str] = None
#     status : Optional[bool] = None
# <- DeviceList ->
class DeviceListBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
# 
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
    # id_device_group: Optional[int] = None
    id_template: Optional[int] = None
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
class DeviceListShortOut(BaseModel):
    id: Optional[int] = None
    name:Optional[str] = None
    rtu_bus_address:Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
    status: Optional[bool] = None
    device_type_name: Optional[str] = None
    driver_type: Optional[str] = None
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
    id_template: Optional[int] = None
    # id_device_group: Optional[int] = None
    
    class Config:
        # allow_population_by_field_name = True
        # populate_by_name = True
        # from_attributes = True
        orm_mode = True

# class DevicePanel(BaseModel):
#     panel:Optional[int] = None
#     class Config:
#         orm_mode = True
# class DeviceString(BaseModel):
#     string_number: Optional[int] = None
#     string: list[DevicePanel]= None
#     class Config:
#         orm_mode = True
# class DeviceMPTT(BaseModel):
#     mppt_number:Optional[int] = None
#     mppt: list[DeviceString] = None
#     class Config:
#         orm_mode = True
class MPPTSTRINGPANEL(BaseModel):
    id: Optional[int] = None
    # name: Optional[str] = None
    id_pointkey: Optional[str] = None
    status : Optional[bool] = None
    class Config:
        orm_mode = True
class MPPTSTRING(BaseModel):
    
    id: Optional[int] = None
    # name: Optional[str] = None
    id_pointkey: Optional[str] = None
    status : Optional[bool] = None
    panel: list[MPPTSTRINGPANEL] = None
    
    class Config:
        orm_mode = True
class MPPTBase(BaseModel):
  
    id: Optional[int] = None
    status : Optional[bool] = None
    # name: Optional[str] = None
    id_pointkey: Optional[str] = None
    string: list[MPPTSTRING] =  None
    
    class Config:
        orm_mode = True
class MultipleDeviceCreate(BaseModel):
    name: Optional[str]  = Field(...,description="") 
    device_virtual: Optional[bool] =  Field(...,examples=[False],description="") 
    # Modbus device connected
    id_communication: Optional[int] = Field(...,description="") 
    rtu_bus_address: Optional[int] = Field(...,) 
    tcp_gateway_port: Optional[int] = Field(...,examples=[502]) 
    tcp_gateway_ip: Optional[str] = Field(...,) 
    id_device_type: Optional[int] = Field(...,) 
    add_count: Optional[int] = Field(...,) 
    in_mode: Optional[int] = Field()
    id_template: Optional[int] = None
    mppt: Optional[list[MPPTBase]] = None
    # 
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
    id: Optional[int] = None
    class Config:
        orm_mode = True
class DeviceDeleteMulti(BaseModel):
    device: list[DeviceDelete]= None
    mode: Optional[int] =   Field(...,examples=[1],description="=1 Deactivate | =2 Delete")
    
    class Config:
        orm_mode = True
class DeviceUpdateBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    # ModBus device connected
    id_communication: Optional[int] = Field(...,) 
    rtu_bus_address: Optional[int] = Field(...,examples=[1]) 
    tcp_gateway_port: Optional[int] = Field(...,examples=[502]) 
    tcp_gateway_ip: Optional[str] = Field(...,examples=["192.168.xxx.xx"]) 
    id_device_type: Optional[int] = Field(...,) 
    id_template: Optional[int] = None
    mode_update : Optional[int] = None
    # id_device_group: Optional[int] = None
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
        orm_mode = True
        
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
class DeviceListOfPointListOut(DeviceListOut):
    point_p_list:Optional[PointBase] = None
    point_q_list:Optional[PointBase] = None
    point_pf_list:Optional[PointBase] = None
    device_type:Optional[DeviceTypeBase]= Field(...,alias='Type')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True

# # <- DeviceConfig ->
class DeviceConfigOut(BaseModel):
    # device_list:list[DeviceListBase]= None
    device_type:list[DeviceTypeBase]= None
    device_group:list[DeviceGroupBase]= None
    communication:list[CommunicationCreate]= None
    template:list[TemplateBase]= None 
    class Config:
        orm_mode = True
class DeviceExistDataOut(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
        
        