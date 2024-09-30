# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional,Any
from pydantic import BaseModel



class PointListControlGroupBase(BaseModel):
    id_template: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    value: Optional[int] = None
    attributes: Optional[int] = None
    status: Optional[int] = None
    class Config:
        orm_mode = True


class PointListControlGroup(PointListControlGroupBase):
    id: Optional[int]= None
class PointListControlGroupsOut(list[PointListControlGroup]):
    pass
    