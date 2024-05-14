from typing import Optional

from pydantic import BaseModel


class DevicePoint(BaseModel):
    id: int
    name: str
    low_alarm: float
    high_alarm: float
    output_values: float
    status: bool


class DevicePointOutput(BaseModel):
    points: list[DevicePoint]
    id_template: int
