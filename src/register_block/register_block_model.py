from typing import Optional

from pydantic import BaseModel


class RegisterBlockBase(BaseModel):
    id_template: Optional[int] = None
    addr: Optional[int] = None
    count: Optional[int] = None
    id_type_function: Optional[int] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class RegisterBlock(RegisterBlockBase):
    id: int

    class Config:
        orm_mode = True


class ValidateRegisterBlock(BaseModel):
    id_template: int
    id_type_function: int
