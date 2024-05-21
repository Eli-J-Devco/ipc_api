# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pydantic.main import BaseModel

from .point_model import PointBase


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
