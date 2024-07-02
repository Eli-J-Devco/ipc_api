import enum
from typing import Optional

from pydantic import BaseModel


class TopicEnum(enum.Enum):
    GET = "SLD/GET"
    WRITE = "SLD/WRITE"
    DEAD_LETTER = "SLD/DEAD_LETTER"


class ActionEnum(enum.Enum):
    GetSLD = 0


class PointType(enum.Enum):
    MPPT = 277
    MPPT_CONFIG = 274
    STRING = 276
    PANEL = 278
    POINT = 266


class Point(BaseModel):
    id: int
    name: str
    id_template: int
    parent: Optional[int] = None
    id_config_information: int


class PointOutput(Point):
    children: Optional[list[Point]] = []


class MetadataModel(BaseModel):
    retry: int


class PayloadModel(BaseModel):
    type: int = 0
    id: Optional[int] = None


class SLDModel(BaseModel):
    metadata: MetadataModel
    payload: PayloadModel


class Communication(BaseModel):
    id: int
    name: str
    id_driver_list: int


class DeviceType(BaseModel):
    id: int
    type: int


class SymbolicDevice(BaseModel):
    id: int
    name: str


class DeviceModel(BaseModel):
    id: int
    name: str

    # communication: Optional[Communication] = None
    # device_type: Optional[DeviceType] = None

    class Config:
        orm_mode = True


class SLDResponseModel(DeviceModel):
    children: Optional[list[DeviceModel]] = []
