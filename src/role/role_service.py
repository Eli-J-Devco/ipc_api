import logging

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .role_filter import UpdateRoleScreenFilter
from .role_model import RoleCreate, RoleScreenMapBase, RoleUpdate
from .role_entity import Role as RoleEntity, RoleScreenMap as RoleScreenMapEntity, UserRoleMap as UserRoleMapEntity
from ..authentication.authentication_model import Permission
from ..project_setup.project_setup_entity import Screen
from ..project_setup.project_setup_service import ProjectSetupService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class RoleService:

    @async_db_request_handler
    async def add_role(self, role: RoleCreate, session: AsyncSession):
        new_role = RoleEntity(
            **role.dict()
        )
        session.add(new_role)

        screens = await ProjectSetupService().get_screens(session)
        if screens:
            for screen in screens:
                role_screen_map = RoleScreenMapBase(
                    id_role=new_role.id,
                    id_screen=screen.id,
                )
                session.add(RoleScreenMapEntity(**role_screen_map.dict()))
        await session.commit()
        return "Role added successfully"

    @async_db_request_handler
    async def get_role(self, session: AsyncSession):
        query = select(RoleEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_role_by_id(self, role_id: int, session: AsyncSession, func=None, *args, **kwargs):
        if not role_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role ID is required")

        query = select(RoleEntity).filter(RoleEntity.id == role_id)
        result = await session.execute(query)
        role = result.scalars().first()

        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(role_id, session, *args, **kwargs)

        return role

    @async_db_request_handler
    async def get_role_by_name(self, role_name: str, session: AsyncSession, func=None, *args, **kwargs):
        if not role_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name is required")

        query = select(RoleEntity).filter(RoleEntity.name == role_name)
        result = await session.execute(query)
        role = result.scalars().first()

        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(role_name, session, *args, **kwargs)

        return role

    @async_db_request_handler
    async def get_role_by_user_id(self, user_id: int, session: AsyncSession):
        query = (select(RoleEntity.id, RoleEntity.name, RoleEntity.description, RoleEntity.status)
                 .join(UserRoleMapEntity, RoleEntity.id == UserRoleMapEntity.id_role)
                 .where(UserRoleMapEntity.id_user == user_id)
                 .where(UserRoleMapEntity.status == 1)
                 .where(RoleEntity.status == 1)
                 )
        result = await session.execute(query)

        roles = []
        for row in result.all():
            roles.append(RoleUpdate(id=row[0], name=row[1], description=row[2], status=row[3]))

        return roles

    @async_db_request_handler
    async def update_role(self, role_id: int, session: AsyncSession, role: RoleUpdate):
        if role.name:
            is_role_name_exist = await self.get_role_by_name(role.name, session)
            if is_role_name_exist.id != role_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")

        updating_role = await self.get_role_by_id(role_id, session)
        updating_role = RoleCreate(**updating_role.__dict__)
        updating_role = updating_role.copy(update=role.dict(exclude_unset=True))

        query = (update(RoleEntity)
                 .where(RoleEntity.id == role_id)
                 .values(updating_role.dict()))
        await session.execute(query)
        await session.commit()
        return "Role updated successfully"

    @async_db_request_handler
    async def delete_role(self, role_id: int, session: AsyncSession):
        query = delete(RoleEntity).where(RoleEntity.id == role_id)
        await session.execute(query)
        await session.commit()
        return "Role deleted successfully"

    @async_db_request_handler
    async def activate_role(self, role_id: int, session: AsyncSession):
        query = (update(RoleEntity)
                 .where(RoleEntity.id == role_id)
                 .values(status=True))
        await session.execute(query)
        await session.commit()
        return "Role activated successfully"

    @async_db_request_handler
    async def deactivate_role(self, role_id: int, session: AsyncSession):
        query = (update(RoleEntity)
                 .where(RoleEntity.id == role_id)
                 .values(status=False))
        await session.execute(query)
        await session.commit()
        return "Role deactivated successfully"

    @async_db_request_handler
    async def get_role_permissions(self, role_id: int, session: AsyncSession):
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

    @async_db_request_handler
    async def update_role_permission(self,
                                     role_id: int,
                                     session: AsyncSession,
                                     role_screen: RoleScreenMapBase):
        query = (update(RoleScreenMapEntity)
                 .where(RoleScreenMapEntity.id_role == role_id)
                 .where(RoleScreenMapEntity.id_screen == role_screen.id_screen)
                 .values(auths=role_screen.auths))
        await session.execute(query)
        await session.commit()
        return "Role permission updated successfully"

    @async_db_request_handler
    async def update_user_role_map(self, user_id: int, role_id: list[int], session: AsyncSession):
        query = delete(UserRoleMapEntity).where(UserRoleMapEntity.id_user == user_id)
        await session.execute(query)

        for role in role_id:
            user_role_map = UserRoleMapEntity(
                id_user=user_id,
                id_role=role,
                status=1
            )
            session.add(user_role_map)
        await session.commit()
        return "User role updated successfully"
