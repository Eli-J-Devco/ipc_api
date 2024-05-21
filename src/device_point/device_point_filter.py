# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic.main import BaseModel


class GetDevicePointMapFilter(BaseModel):
    id: int


class PointActionFilter(BaseModel):
    id_device: int
    id_devices_to_config: Optional[list[int]] = None
    id_point: list[int]
    action: str


class AlarmValue(BaseModel):
    id_point: int
    low_alarm: float
    high_alarm: float


class AlarmValueUpdateFilter(BaseModel):
    id_device: int
    values: list[AlarmValue]


class PointUpdateFilter(BaseModel):
    id: int
    id_device: int
    id_type_units: int
    id_point_list: int
    name: str
