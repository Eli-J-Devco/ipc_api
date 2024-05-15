from pydantic.main import BaseModel


class PointFilter(BaseModel):
    id: int


class GetPointFilter(BaseModel):
    id_template: int


class DeletePointFilter(GetPointFilter):
    id_points: int | list[int]


class AddPointFilter(GetPointFilter):
    num_of_points: int


class UpdatePointUnitFilter(PointFilter):
    unit: int
