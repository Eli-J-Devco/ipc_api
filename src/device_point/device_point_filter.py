from typing import Optional

from pydantic.main import BaseModel


class GetDevicePointMapFilter(BaseModel):
    id: int


class PointActionFilter(BaseModel):
    id_device: int
    id_devices_to_config: Optional[list[int]] = None
    id_point: list[int]
    action: str

