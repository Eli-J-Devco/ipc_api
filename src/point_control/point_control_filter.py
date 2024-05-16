from typing import Optional

from pydantic.main import BaseModel


class ControlGroupBaseFilter(BaseModel):
    name: str
    id_template: int
    description: Optional[str] = None
    attributes: Optional[int] = 0


class PointControlBase(BaseModel):
    id_control_group: Optional[int] = None


class PointControlAddFilter(PointControlBase):
    id_point: int


class PointsControlAddFilter(PointControlBase):
    id_points: list[int]


class ControlGroupAddFilter(ControlGroupBaseFilter):
    id_points: Optional[list[int]] = []
