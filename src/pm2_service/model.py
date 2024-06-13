import enum
from typing import Optional

from pydantic import BaseModel


class CreateCodeEnum(enum.Enum):
    CreateRS485Dev = 1
    CreateTCPDev = 3


class DeleteCodeEnum(enum.Enum):
    DELETE_DEV = "DeleteDev"


class CodeEnum(enum.Enum):
    CREATE = CreateCodeEnum
    DELETE = DeleteCodeEnum


class DeviceModel(BaseModel):
    id: int
    name: str
    connect_type: Optional[str] = None
    id_communication: Optional[int] = None
    mode: int = 0
    device_type_value: int = 0


class PayloadModel(BaseModel):
    id: Optional[int] = None
    id_communication: Optional[int] = None
    device: Optional[list[DeviceModel]] = None
    delete_mode: Optional[int] = None


class MessageModel(BaseModel):
    CODE: str
    PAYLOAD: PayloadModel
