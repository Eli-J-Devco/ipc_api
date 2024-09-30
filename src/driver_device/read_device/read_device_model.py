# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional, Any
from pydantic.fields import Field
from pydantic import BaseModel

class ReadRegisterDevice(BaseModel):
    code: Optional[int] = None
    data: Optional[list] = []
    exception_code: Optional[str] = None
    address: Optional[int] = None
    
class StatusRB(BaseModel):
    address: Optional[int] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
class StatusRBs(list[StatusRB]):
    pass
    
class RegisterData(BaseModel): 
    mra: Optional[int] = None
    value: Optional[float] = None
    func: Optional[int] = None
    
class MergeRegisterDevice(BaseModel): 
    status_device: Optional[str] = None
    status_rb: list[StatusRB]=[]
    data: list[RegisterData]=[]
    
class RegisterValueDevice(BaseModel):     
    data: list[RegisterData]=[]
    status_rb: list[StatusRB]=[]
    read_status_rb: list[str]=[]
    status_device: Optional[str] = None
    timestamp: Optional[str] = None
    message : Optional[str] = None
    
class PointDataBase(BaseModel):
    config: Optional[str] = None
    id_point_list_type: Optional[int] = None
    name_point_list_type: Optional[str] = None
    id_point: Optional[int] = None
    parent: Optional[int] = None
    id: Optional[int] = None
    point_key: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    value: Optional[Any] = None
    quality: Optional[int] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None 
    active: Optional[int] = None
    id_control_group: Optional[int] = None
    control_type_input: Optional[int] = None
    control_menu_order: Optional[int] = None
    control_min: Optional[float] = None
    control_max: Optional[float] = None
    control_enabled: Optional[int] = None # show/hide = 1/0, get from Device
    panel_height: Optional[float] = None
    panel_width: Optional[float] = None
    output_values: Optional[float] = None
    slope: Optional[float] = None
    
    
class PointDataOut(list[PointDataBase]):
    pass