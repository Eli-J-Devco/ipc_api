import enum
from typing import Optional

from pydantic import BaseModel


class MetadataModel(BaseModel):
    retry: int


class CreateDeviceModel(BaseModel):
    metadata: MetadataModel
    type: str
    devices: list[int]


class DeviceState(enum.Enum):
    CREATING = 1
    CREATED = 2
    DELETING = 3
    DELETED = 4
    DEAD_LETTER = 5


class Action(enum.Enum):
    CREATE = "InitDevices/create"
    UPDATE = "InitDevices/update"
    DELETE = "InitDevices/delete"
    DEAD_LETTER = "InitDevices/dead-letter"
    SET_PROJECT_MODE = "InitDevices/set-project-mode"


class Point(BaseModel):
    id: int
    parent: Optional[int] = None
    id_pointkey: str
    name: str
    id_config_information: int
    id_control_group: Optional[int] = None


class PointString(Point):
    children: Optional[list[Point]] = []


class PointMPPT(Point):
    children: Optional[list[PointString]] = []


class Communication(BaseModel):
    id: int
    name: str


class DeviceType(BaseModel):
    id: int
    type: int


class DeviceModel(BaseModel):
    id: int
    name: str
    table_name: Optional[str] = None
    view_table: Optional[str] = None
    id_template: Optional[int] = None

    points: Optional[list[Point]] = None
    communication: Optional[Communication] = None
    device_type: Optional[DeviceType] = None

    class Config:
        orm_mode = True


class PointType(enum.Enum):
    MPPT = 277
    STRING = 276
    PANEL = 278
    POINT = 266


class DeviceMppt(BaseModel):
    id: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None


class DeviceMpptString(BaseModel):
    id: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    id_device_mppt: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    panel: Optional[int] = None


class DevicePanel(BaseModel):
    id: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    id_device_string: Optional[int] = None
    name: Optional[str] = None


class DevicePointListMap(BaseModel):
    id: Optional[int] = None
    id_device_list: Optional[int] = None
    id_point_list: Optional[int] = None
    name: Optional[str] = None

