# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import enum
from datetime import date
from typing import Optional

from pydantic.main import BaseModel


class CodeEnum(enum.Enum):
    CreateRS485Dev = 1
    CreateTCPDev = 3
    DeleteDev = 0
    UpdateDev = -1
    UpdateTemplate = -2


class IncreaseMode:
    TCP: int = 1
    RTU: int = 2


class AddDevicesModeFilter(BaseModel):
    num_of_devices: Optional[int] = 1
    inc_mode: Optional[int] = 1


class AddInverterFilter(BaseModel):
    rated_power: Optional[float] = 0.0
    mode: Optional[int] = 0


class AddMeterFilter(BaseModel):
    meter_type: Optional[int] = 0


class AddDevicesFilter(AddDevicesModeFilter, AddInverterFilter, AddMeterFilter):
    name: str
    id_device_type: int
    id_device_group: int
    id_template: int
    id_communication: int
    device_virtual: bool
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None


class GetDeviceFilter(BaseModel):
    id_template: Optional[int] = None
    id_device: Optional[int] = None


class UpdateDeviceFilter(BaseModel):
    id: int
    name: str
    rtu_bus_address: int
    tcp_gateway_ip: str
    tcp_gateway_port: int
    rated_power: float
    rated_power_custom: float
    min_watt_in_percent: float
    DC_voltage: float
    DC_current: float
    mode: int
    efficiency: float
    enable_poweroff: Optional[bool] = None
    inverter_shutdown: Optional[date] = None
    DC_voltage: float
    DC_current: float

class AddDeviceGroupFilter(BaseModel):
    id_device_type: int
    name: str
