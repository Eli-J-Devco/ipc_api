# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic import BaseModel

from ..point.point_model import PointOutput
from ..project_setup.project_setup_model import ConfigInformationShort


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
    children: Optional[list[PointOutput]] = None

    class Config:
        orm_mode = True


class PointConfigFull(BaseModel):
    data_type: Optional[list[ConfigInformationShort]] = None
    byte_order: Optional[list[ConfigInformationShort]] = None
    point_unit: Optional[list[ConfigInformationShort]] = None
    type_point: Optional[list[ConfigInformationShort]] = None
    type_point_list: Optional[list[ConfigInformationShort]] = None
    type_class: Optional[list[ConfigInformationShort]] = None

    class Config:
        orm_mode = True
