# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import enum

from pydantic.main import BaseModel

from .point_model import PointBase


class ControlInputType(enum.Enum):
    NotImplemented = 0
    Number = 1
    String = 2
    Percent = 3
    Bool = 4


class PointFilter(BaseModel):
    id: int


class GetPointFilter(BaseModel):
    id_template: int


class DeletePointFilter(GetPointFilter):
    id_points: int | list[int]


class AddPointFilter(GetPointFilter):
    num_of_points: int


class AddPointListFilter(GetPointFilter):
    point: list[PointBase]


class UpdatePointUnitFilter(PointFilter):
    unit: int
