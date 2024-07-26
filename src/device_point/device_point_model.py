# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic import BaseModel


class EnableField(BaseModel):
    name: bool
    unit: bool


class PointUnit(BaseModel):
    id: int
    name: str


class DevicePoint(BaseModel):
    id: int
    id_point_list: int
    name: str
    unit: Optional[PointUnit] = None
    low_alarm: float
    high_alarm: float
    control_min: float
    control_max: float
    output_values: float
    status: bool
    enable_edit: EnableField


class TemplatePoint(BaseModel):
    id: int
    type: int


class DevicePointOutput(BaseModel):
    points: list[DevicePoint]
    # template: TemplatePoint
