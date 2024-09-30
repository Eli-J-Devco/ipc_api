# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic import BaseModel


class RegisterBlockBase(BaseModel):
    id_template: Optional[int] = None
    addr: Optional[int] = 65535
    count: Optional[int] = 0
    # id_type_function: Optional[int] = 269
    # status: Optional[bool] = True

    class Config:
        orm_mode = True


class RegisterBlock(RegisterBlockBase):
    id: Optional[int]= None
    template_name: Optional[str] = None
    namekey: Optional[str] = None
    Functions: Optional[int] = None
    class Config:
        orm_mode = True


class ValidateRegisterBlock(BaseModel):
    id_template: int
    id_type_function: int

class RegisterBlockOutput(BaseModel):
    registerblock: Optional[list[RegisterBlock]]= None