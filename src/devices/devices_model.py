# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import enum
from typing import Optional

from pydantic import BaseModel


class DeviceFull(BaseModel):
    id: Optional[int] = None
    table_name: Optional[str] = None
    view_table: Optional[str] = None
    name: Optional[str] = None
    device_virtual: Optional[bool] = False
    id_project_setup: Optional[int] = 1
    id_device_type: Optional[int] = None
    id_communication: Optional[int] = None
    id_template: Optional[int] = None
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
    enable: Optional[bool] = False

    rated_power: Optional[float] = 1500.0
    rated_power_custom: Optional[float] = 1500.0
    min_watt_in_percent: Optional[float] = 5.0
    DC_voltage: Optional[float] = 400.0
    DC_current: Optional[float] = 10.0
    compensate_watt_factor: Optional[float] = 1.0
    battery_mode: Optional[int] = 1
    battery_normal_watt: Optional[float] = 1500.0
    battery_reduce_watt: Optional[float] = 300.0
    battery_threshold_off_limit_in_v: Optional[float] = 47.0
    battery_threshold_reduce_limit_in_v: Optional[float] = 48.0
    battery_threshold_normal_limit_in_v: Optional[float] = 48.5
    battery_threshold_on_limit_in_v: Optional[float] = 51.0
    battery_priority: Optional[int] = 0

    point: Optional[int] = None
    pv: Optional[int] = 16
    mode: Optional[int] = 0
    model: Optional[int] = 0
    function: Optional[str] = None
    point_p: Optional[int] = None
    value_p: Optional[float] = 100.0
    send_p: Optional[int] = 0

    point_q: Optional[int] = None
    value_q: Optional[float] = 100.0
    send_q: Optional[int] = 0

    point_pf: Optional[int] = None
    value_pf: Optional[float] = 1.0
    send_pf: Optional[int] = 0

    max: Optional[float] = None
    allow_error: Optional[float] = None
    efficiency: Optional[float] = 98
    enable_poweroff: Optional[bool] = 0
    inverter_shutdown: Optional[datetime.date] = None
    meter_type: Optional[int] = None
    inverter_type: Optional[int] = 2
    status: Optional[bool] = True
    driver_type: Optional[str] = None
    device_type: Optional[str] = None


class Devices(BaseModel):
    id: int
    name: str


class DeviceUploadChannelMap(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class DeviceType(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class DeviceGroup(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Action(enum.Enum):
    CREATE = "InitDevices/create"
    UPDATE = "InitDevices/update"
    DELETE = "InitDevices/delete"
    DEAD_LETTER = "InitDevices/dead-letter"


class DeviceConfigOutput(BaseModel):
    device_types: list[DeviceType]
    device_groups: list[DeviceGroup]
