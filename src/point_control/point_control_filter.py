# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic.main import BaseModel


# region Control Group
class GetControlGroupFilter(BaseModel):
    id_template: Optional[int] = None


class ControlGroupBaseFilter(BaseModel):
    name: str
    id_template: int
    description: Optional[str] = None
    attributes: Optional[int] = 0


class ControlGroupAddFilter(ControlGroupBaseFilter):
    id_points: Optional[list[int]] = []
    add_type: Optional[int] = None


class ControlGroupUpdateFilter(ControlGroupBaseFilter):
    id: int


class ControlGroupDeleteFilter(BaseModel):
    id_template: int
    id_group: list[int] = []
    id_points: Optional[list[int]] = []
# endregion


class PointControlBase(BaseModel):
    id_template: Optional[int] = None
    id_control_group: Optional[int] = None


class PointControlAddFilter(PointControlBase):
    id_point: int


class PointsControlAddFilter(PointControlBase):
    id_points: list[int]


class PointControlCreateFilter(PointControlBase):
    is_clone_from_last: bool = False
    number_of_points: int = 0


class PointRemoveFilter(BaseModel):
    id_template: int
    id_points: list[int]

