from ..point.point_model import PointBase


class PointMpptBase(PointBase):
    pass


class PointString(PointMpptBase):
    children: list[PointMpptBase] = []


class PointMppt(PointMpptBase):
    children: list[PointString | PointMpptBase] = []

    class Config:
        orm_mode = True

