import enum
from typing import Optional

from pydantic.main import BaseModel


class CodeEnum(enum.Enum):
    CreateRS485Dev = 1
    CreateTCPDev = 3
    DeleteDev = 0


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
