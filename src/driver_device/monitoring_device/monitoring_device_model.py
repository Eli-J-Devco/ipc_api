# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional, Any
from pydantic.fields import Field
from pydantic import BaseModel
import enum
from src.driver_device.read_device.read_device_model import PointDataBase,PointDataOut
class Action(enum.Enum):
    WMaxPercent = "WMaxPercent"
    WMaxPercentEnable = "WMaxPercentEnable"
    VarMaxPercent = "VarMaxPercent"
    VarMaxPercentEnable= "VarMaxPercentEnable"
    ACPowerFactor= "ACPowerFactor"
    WMax= "WMax"
    VarMax= "VarMax"
class DeviceTypeAction(enum.Enum):
    PVSystemInverter = "PV System Inverter"
    

    
# class ControlGroupUpdate(BaseModel):
#     # step 1 get from DB output_values
#     # step 2 update in control 
#     power_limit_percent: Optional[float] = None
#     power_limit_percent_enable: Optional[int] = None
    
#     reactive_limit_percent: Optional[float] = None
#     reactive_limit_percent_enable: Optional[int] = None
#     # step 1 get from DB
#     # step 2 update in control 
#     mode : Optional[int] = None
    
    

class MonitoringDeviceBase(BaseModel):
    memory:Optional[Any] = None
    id_device:Optional[int] = None
    id_device_group: Optional[int] = None
    parent: Optional[Any] = None
    
    mode: Optional[int] = None
    device_name: Optional[str] = None
    id_device_type: Optional[int] = None
    name_device_type: Optional[str] = None
    type_device_type: Optional[int] = None
    
    meter_type: Optional[int] = None
    inverter_type: Optional[int] = None
    
    status_device: Optional[str] = None
    
    timestamp: Optional[str] = None
    message: Optional[str] = None
    status_register: list[Any] = []
    
    point_count: Optional[int] = None
    parameters: list[Any] = []
    fields: list[Any] = []
    mppt: list[Any] = []
    combiner_box: list[Any] = []
    control_group: list[Any] = []
    rated_power: Optional[Any] = None
    rated_power_custom: Optional[Any] = None
    min_watt_in_percent: Optional[Any] = None
    emergency_stop: Optional[Any] = None
    rtu_bus_address: Optional[int] = None

    rated_power_custom_calculator: Optional[float] =None
    rated_reactive_custom: Optional[float] =None


class MonitoringParameterBase(BaseModel):
    id:Optional[int] = None
    name: Optional[str] = None
    fields: PointDataOut=[]
class MonitoringParameters(list[MonitoringParameterBase]):
    pass


class MonitoringPointControlGroup(BaseModel):
    id:Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    attributes:Optional[int] = None
    fields: list[Any] = []
class MonitoringPointControlGroups(list[MonitoringPointControlGroup]):
    pass