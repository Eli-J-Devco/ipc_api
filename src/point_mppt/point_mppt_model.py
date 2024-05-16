from ..point.point_model import PointOutput


class PointMpptBase(PointOutput):
    pass


class PointString(PointMpptBase):
    children: list[PointMpptBase] = []


class PointMppt(PointMpptBase):
    children: list[PointString | PointMpptBase] = []

    class Config:
        orm_mode = True

