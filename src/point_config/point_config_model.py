from typing import Optional

from pydantic import BaseModel

from ..point.point_model import PointBase


class PointListType(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class PointclassType(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class PointListControlGroup(BaseModel):
    id: Optional[int] = None
    id_template: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    value: Optional[int] = None
    attributes: Optional[int] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class PointListControlGroupChildren(PointListControlGroup):
    children: Optional[list[PointBase]] = None
    class Config:
        orm_mode = True