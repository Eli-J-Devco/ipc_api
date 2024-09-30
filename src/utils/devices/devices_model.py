# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import enum
from typing import Optional

from pydantic import BaseModel

class Devices(BaseModel):
    id: int
    id_device_type: int
    name: str
class ParameterListUpdate(enum.Enum):
    
    parameters={"rtu_bus_address",
                "tcp_gateway_ip",
                "tcp_gateway_port",
                "mode",
                "rated_power",
                "rated_power_custom",
                "min_watt_in_percent",
                "DC_voltage",
                "DC_current"
                } 
    
    
    
class DeviceFull(BaseModel):
    id: Optional[int] = None
    parent: Optional[int] = None
    name: Optional[str] = None
    mode: Optional[int] = None
    id_template: Optional[int] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
    
    point_p: Optional[int] = None
    value_p: Optional[float] = None
    send_p:Optional[int] = None
    
    point_q: Optional[int] = None
    value_q: Optional[float] = None
    send_q:Optional[int] = None
    
    point_pf: Optional[int] = None
    value_pf: Optional[float] =None
    send_pf:Optional[int] = None
    
    enable_poweroff: Optional[bool] = None
    inverter_shutdown: Optional[datetime.date] = None
    
    connect_type: Optional[str] = None
    device_type: Optional[str] = None
    id_device_type:Optional[int] = None
    type_device_type:Optional[int] = None
    
    device_group: Optional[str] = None
    id_device_group:Optional[int] = None
    
    template_name: Optional[str] = None
    
    rated_power: Optional[float] =None
    rated_power_custom: Optional[float] =None
    min_watt_in_percent: Optional[float] =None
    meter_type: Optional[int] = None
    DC_voltage: Optional[float] =None
    DC_current: Optional[float] =None
    inverter_type: Optional[int] = None
    device_parent: Optional[int] = None
    emergency_stop: Optional[int] = None
    
    rated_power_custom_calculator: Optional[float] =None
    rated_reactive_custom: Optional[float] =None
    
class DeviceInit(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    connect_type: Optional[str] = None
    device_type: Optional[str] = None
    type: Optional[int] = None
    id_communication: Optional[int] = None
    
class DeviceInitOutput(BaseModel):
    devices: Optional[list[DeviceInit]]= None

class Action(enum.Enum):
    TCP = "Modbus/TCP"
    RS485 = "RS485"
    BACnet = "BACnet"
    DNP3_TCP= "DNP3_TCP"
    DNP3_SERIAL= "DNP3_Serial"
