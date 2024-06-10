# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field


class SldGroupBase(BaseModel):
    name: Optional[str] = None
    type: Optional[int] = None
    status: Optional[bool] = True
    class Config:
        orm_mode = True
class SldGroupUpdate(SldGroupBase):
    id: Optional[int] = None
    class Config:
        orm_mode = True
class SldGroupResponse(BaseModel):
    code: str
    status: int
    payload: Optional[SldGroupUpdate] = None
