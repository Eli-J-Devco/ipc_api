# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional
from pydantic import BaseModel


class PointListType(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    class Config:
        orm_mode = True

class PointListTypes(list[PointListType]):
    pass