from typing import Optional
from pydantic import BaseModel

class DeviceMPPTStringModel(BaseModel):
    id_device_list: int
    namekey: str
    current: float

    class Config:
        orm_mode = True