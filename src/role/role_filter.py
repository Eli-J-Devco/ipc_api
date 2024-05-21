# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pydantic.main import BaseModel


class RoleScreenFilter(BaseModel):
    id: int
    auth: int


class UpdateRoleScreenFilter(BaseModel):
    id_role: int
    role_screen: list[RoleScreenFilter]
