from typing import Optional
from pydantic import BaseModel

class DeviceMPPTModel(BaseModel):
    id_device_list: int
    namekey: str
    voltage: float
    current: float

    class Config:
        orm_mode = True