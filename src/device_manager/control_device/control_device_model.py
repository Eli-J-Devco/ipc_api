# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional,Any
from pydantic.fields import Field
from pydantic import BaseModel


class ControlParameter(BaseModel):
    id_pointkey: Optional[str] = None
    
    datatype: Optional[int] = None
    modbus_func: Optional[int] = None
    register_value: Optional[int] =None# Field(None, alias="registers")
    value: Optional[Any] = None
    
class ControlDevice(BaseModel):
    id_device: Optional[int] = None
    id_device_group: Optional[int] = None
    mode: Optional[int] = None
    rated_power: Optional[float] = None
    rated_power_custom: Optional[float] = None
    parameter: Optional[list[ControlParameter]] = None
    token: Optional[str] = None
    
    
    time : Optional[str] = None
    status: Optional[str] = None
    setpoint: Optional[Any] = None
    feedback: Optional[Any] = None
class ControlModeDevice(BaseModel):
    id_device: Optional[int] = None
    time_stamp : Optional[str] = None
    status: Optional[str] = None
    confirm_mode: Optional[int] = None
    token: Optional[str] = None
class ControlDevices(list[ControlDevice]):
    pass




