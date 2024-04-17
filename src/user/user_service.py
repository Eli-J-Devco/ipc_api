import logging

from .user_model import User
from .user_entity import User as UserEntity
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..authentication.authentication_model import Permission
from ..user.user_entity import (UserRoleMap as UserRoleMapEntity,
                                RoleScreenMap as RoleScreenMapEntity)
from ..project_setup.project_setup_entity import Screen


@Injectable
class UserService:

    @async_db_request_handler
    async def add_user(self, user: User, session: AsyncSession):
        new_user = UserEntity(
            **user.dict()
        )
        session.add(new_user)
        await session.commit()
        return new_user.id

    @async_db_request_handler
    async def get_user(self, session: AsyncSession):
        query = select(UserEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_user_roles(self, user_id: int, session: AsyncSession):
        logging.info(f"===================={user_id}====================")
        query = select(UserRoleMapEntity.id_role).where(UserRoleMapEntity.id_user == user_id)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_user_permissions(self, role_id: int, session: AsyncSession):
        query = (select(RoleScreenMapEntity.id_screen,
                        Screen.screen_name,
                        Screen.description,
                        RoleScreenMapEntity.auths)
                 .join(Screen, RoleScreenMapEntity.id_screen == Screen.id)
                 .where(RoleScreenMapEntity.id_role == role_id)
                 .where(RoleScreenMapEntity.status == 1)
                 .where(Screen.status == 1)
                 )
        result = await session.execute(query)

        permissions = []
        for row in result.all():
            permissions.append(Permission(id=row[0], name=row[1], description=row[2], auth=row[3]))
        return permissions
