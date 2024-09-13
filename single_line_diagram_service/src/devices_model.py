import enum
from typing import Optional

from pydantic import BaseModel

from .devices_entity import (DeviceMppt as DeviceMpptEntity,
                             DeviceMpptString as DeviceMpptStringEntity,
                             DevicePanel as DevicePanelEntity)


class TopicEnum(enum.Enum):
    GET = "SLD/GET"
    WRITE = "SLD/WRITE"
    DEAD_LETTER = "SLD/DEAD_LETTER"


class ActionEnum(enum.Enum):
    GetSLD = 0


class PointType(enum.Enum):
    MPPT = 277
    MPPT_CONFIG = 274, 275
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
    parent: Optional[int] = None
    id_device_type: Optional[int] = None
    plug_point: Optional[int] = None

    # communication: Optional[Communication] = None
    # device_type: Optional[DeviceType] = None

    class Config:
        orm_mode = True


class DevicePointBase(BaseModel):
    id: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    parent: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None


class DevicePanel(DevicePointBase):
    pass


class DeviceMpptString(DevicePointBase):
    # num_of_panels: Optional[int] = None
    children: Optional[list[DevicePanel]] = []


class DeviceMppt(DevicePointBase):
    children: Optional[list[DeviceMpptString]] = []


class SLDResponseModel(DeviceModel):
    children: Optional[list[DeviceModel]] = []


class DeviceConnection(BaseModel):
    device_list_id: int
    device_table: str
    connect_device_id: int
    connect_device_table: str
    type: Optional[int] = None


class DeviceConnectionEntityEnum(enum.Enum):
    device_mppt = DeviceMpptEntity
    device_mppt_string = DeviceMpptStringEntity
    device_panel = DevicePanelEntity


class DeviceConnectionEnum(enum.Enum):
    device_mppt = DeviceMppt
    device_mppt_string = DeviceMpptString
    device_panel = DevicePanel
