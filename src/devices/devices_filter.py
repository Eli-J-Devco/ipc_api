from typing import Optional

from pydantic.main import BaseModel


class IncreaseMode:
    TCP: int = 1
    RTU: int = 2


class AddDevicesModeFilter(BaseModel):
    num_of_devices: Optional[int] = 1
    mode: Optional[int] = 1


class AddDevicesFilter(AddDevicesModeFilter):
    name: str
    id_device_type: int
    id_device_group: int
    id_template: int
    id_communication: int
    device_virtual: bool
    rtu_bus_address: Optional[int] = None
    tcp_gateway_ip: Optional[str] = None
    tcp_gateway_port: Optional[int] = None
