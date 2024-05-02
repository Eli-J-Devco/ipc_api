from typing import Optional

from pydantic.main import BaseModel


class PointControlBase(BaseModel):
    id_control_group: Optional[int] = None


class PointControlAddFilter(PointControlBase):
    id_point: int


class PointsControlAddFilter(PointControlBase):
    id_points: list[int]
