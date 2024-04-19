from typing import Optional

from pydantic import BaseModel


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
