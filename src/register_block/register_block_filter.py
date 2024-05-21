# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pydantic.main import BaseModel

from .register_block_model import RegisterBlock


class GetRegisterBlockFilter(BaseModel):
    id_template: int


class AddRegisterBlocksFilter(BaseModel):
    num_of_register_blocks: int
    id_template: int


class DeleteRegisterBlockFilter(BaseModel):
    id_template: int
    id_register_block: int | list[int]


class UpdateRegisterBlockFilter(BaseModel):
    id_template: int
    register_blocks: RegisterBlock | list[RegisterBlock]
