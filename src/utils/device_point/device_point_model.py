# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional,Any
from pydantic.fields import Field
from pydantic import BaseModel


class EnableField(BaseModel):
    name: bool
    unit: bool

class PointUnit(BaseModel):
    id: int
    name: str

class DevicePoint(BaseModel):
    id: int
    id_point_list: int
    name: str
    unit: Optional[PointUnit] = None
    low_alarm: float
    high_alarm: float
    output_values: float
    status: bool
    enable_edit: EnableField

class TemplatePoint(BaseModel):
    id: int
    type: int

class DevicePointBase(BaseModel):
    id: int
    pointkey: Optional[str] = None
    id_point_list_type: Optional[int] = None
    name_point_list_type: Optional[str] = None
    
    pointtype: Optional[str] = None
    id_pointclass: Optional[str] = None
    id_config_infor: Optional[str] = None
    id_pointtype: Optional[str] = None
    
    pointclass : Optional[str] = None
    config_information: Optional[str] = None
    
    id_point: Optional[int] = None
    parent: Optional[int] = None
    name: Optional[str] = None
    low_alarm: Optional[float] = None
    high_alarm: Optional[float] = None
    output_values: Optional[float] = None
    connect_type: Optional[str] = None
    device_type: Optional[str] = None
    device_group: Optional[str] = None
    
    template_name: Optional[str] = None
    id_template: Optional[int] = None
    id_device_group: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    
    id_pointkey: Optional[str] = None
    point_name: Optional[str] = None
    nameedit: Optional[int] = None
    id_type_units: Optional[int] = None
    nameedit: Optional[int] = None
    unitsedit: Optional[int] = None
    
    func: Optional[int] = None
    # register: Optional[int] = None
    register_value: Optional[int] = Field(None, alias="register")
    id_type_datatype: Optional[int] = None
    id_type_byteorder: Optional[int] = None
    slope: Optional[float] = None
    slopeenabled: Optional[int] = None
    offset: Optional[float] = None
    offsetenabled: Optional[int] = None
    multreg: Optional[int] = None
    multregenabled: Optional[int] = None
    userscaleenabled: Optional[int] = None
    invalidvalue: Optional[int] = None
    invalidvalueenabled: Optional[int] = None
    extendednumpoints: Optional[int] = None
    extendedregblocks: Optional[int] = None
    
    value_byteorder: Optional[int] = None
    name_byteorder: Optional[str] = None
    value_datatype: Optional[int] = None
    name_datatype: Optional[str] = None
    value_units: Optional[int] = None
    name_units: Optional[str] = None
    active: Optional[int] = None
    id_control_group: Optional[int] = None
    control_type_input: Optional[int] = None
    control_menu_order: Optional[int] = None
    control_min: Optional[float] = None
    control_max: Optional[float] = None
    panel_height: Optional[float] = None
    panel_width: Optional[float] = None
    constants: Optional[str] = None
class DevicePointsOutput(BaseModel):
    points: list[DevicePointBase]=[]
    # template: TemplatePoint
class ControlPointBase(BaseModel):
    id_control_group : Optional[int] = None
    name : Optional[str] = Field(None, alias="name")
    point_key : Optional[str] = Field(None, alias="pointkey")
    value: Optional[Any] = Field(None, alias="output_values")
    control_min: Optional[float] = None
    control_max: Optional[float] = None
    low_alarm: Optional[float] = None
    high_alarm: Optional[float] = None

class ControlPoints(list[ControlPointBase]):
    pass

class StringBase(BaseModel):
    point_key: Optional[str] = None
    name: Optional[str] = None
    value: Optional[float] = None 
    area: Optional[float] = None 
    number_panel: Optional[int] = None 
class Strings(list[StringBase]):
    pass
class MPPTString(BaseModel):
    mppt_volt: Optional[float] = None 
    mppt_amps: Optional[float] = None 
    mppt_string: Optional[Strings]=None
    
class MPPT(BaseModel):
    config: Optional[str] = None
    id_point: Optional[int] = None
    parent: Optional[int] = None
    id: Optional[int] = None
    point_key: Optional[str] = None
    name: Optional[str] = None
    power: Optional[float] = None
    area: Optional[float] = None 
    irradiance: Optional[float] = None 
    number_panel: Optional[int] = None 
    DC_voltage_max: Optional[float] = None 
    DC_current_max: Optional[float] = None 
    value: Optional[MPPTString]=None

class MPPTs(list[MPPT]):
    pass
# mqtt


