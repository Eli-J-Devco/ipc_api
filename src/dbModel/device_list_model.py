from typing import Optional
from pydantic import BaseModel

class DeviceModel(BaseModel):
    id: int
    name: str
    rtu_bus_address: Optional[int] = None
    rated_power: Optional[float] = None
    mode: Optional[int] = None
    id_device_type: Optional[int] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True