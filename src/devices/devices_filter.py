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


class ActionEnum(enum.Enum):
    Default = 0
    Utils = 1


class IncreaseMode:
    TCP: int = 1
    RTU: int = 2


class SymbolicDevice(BaseModel):
    id: int
    name: str


class AddDevicesModeFilter(BaseModel):
    num_of_devices: Optional[int] = 1
    inc_mode: Optional[int] = 1


class AddInverterFilter(BaseModel):
    rated_power: Optional[float] = 0.0
    mode: Optional[int] = 0
    inverter_type: Optional[int] = None


class AddMeterFilter(BaseModel):
    meter_type: Optional[int] = None


class DeviceComponentFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    id_device_type: Optional[int] = None
    id_device_group: Optional[int] = None
    type: Optional[int] = None


class AddComponentFilter(BaseModel):
    components: Optional[list[DeviceComponentFilter]] = None


class DeviceSecret(BaseModel):
    secret: Optional[str] = None


class RetryCreateDevice(BaseModel):
    is_retry: Optional[bool] = False
    devices: Optional[list[int]] = None


class AddDevicesFilter(AddDevicesModeFilter,
                       AddInverterFilter,
                       AddMeterFilter,
                       AddComponentFilter,
                       DeviceSecret,
                       RetryCreateDevice):
    name: Optional[str] = None
    id_device_type: Optional[int] = None
    id_device_group: Optional[int] = None
    id_template: Optional[int] = None
    id_communication: Optional[int] = None
    device_virtual: Optional[bool] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None


class GetDeviceFilter(BaseModel):
    id_template: Optional[int] = None
    id_device: Optional[int] = None


class ListDeviceFilter(BaseModel):
    id: Optional[int] = None


class UpdateDeviceFilter(AddComponentFilter):
    id: int
    name: str
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
    rated_power: Optional[float] = None
    rated_power_custom: Optional[float] = None
    min_watt_in_percent: Optional[float] = None
    DC_voltage: Optional[float] = None
    DC_current: Optional[float] = None
    mode: Optional[int] = None
    efficiency: Optional[float] = None
    enable_poweroff: Optional[bool] = None
    inverter_shutdown: Optional[date] = None


class AddDeviceGroupFilter(BaseModel):
    id_device_type: int
    name: str


# class DeviceComponentFilter(BaseModel):
#     type: Optional[int] = None


class GetDeviceComponentFilter(DeviceComponentFilter):
    main_type: int
    sub_type: Optional[int] = None


class DeleteDeviceFilter(DeviceSecret):
    device_id: int | list[int] = None
