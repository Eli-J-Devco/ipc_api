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
    CREATE = "devices/create"
    DELETE = "devices/delete"
    DEAD_LETTER = "devices/dead-letter"


class Point(BaseModel):
    id_pointkey: str


class DeviceModel(BaseModel):
    id: int
    table_name: str
    view_table: Optional[str] = None
    id_template: int

    points: Optional[list[Point]] = None


