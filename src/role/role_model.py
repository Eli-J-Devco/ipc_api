from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    id: Optional[int] = None


class RoleCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = True


class RoleUpdate(RoleBase, RoleCreate):
    pass


class RoleScreenMapBase(BaseModel):
    id_role: int
    id_screen: int
    auths: int = 8
    status: Optional[bool] = True


class UserRoleMapBase(BaseModel):
    id_role: int
    id_user: int
    status: bool
