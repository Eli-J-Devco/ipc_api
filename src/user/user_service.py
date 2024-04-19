import random
import string
from datetime import datetime

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from .user_model import UserCreate, UserFull, UserUpdate, UserUpdatePassword
from .user_entity import User as UserEntity

from ..config import env_config
from ..role.role_entity import (UserRoleMap as UserRoleMapEntity,)
from ..role.role_model import UserRoleMapBase
from ..utils.PaginationModel import Pagination
from ..utils.password_hasher import hash_password
from ..utils.service_wrapper import ServiceWrapper
from ..utils.password_hasher import verify
from ..utils.utils import validate_email, validate_phone, validate_password, generate_pagination_response


@Injectable
class UserService:

    @async_db_request_handler
    async def add_user(self, user: UserCreate, session: AsyncSession):
        validate_email(user.email)
        validate_password(user.password)

        if user.phone:
            validate_phone(user.phone)

        hashed_password = hash_password(user.password)

        user_full = UserFull(**user.dict())

        user_full.password = hashed_password

        create_date = datetime.now()
        user_full.create_date = create_date
        user_full.updated_date = create_date

        new_user = UserEntity(
            **user_full.dict()
        )

        session.add(new_user)
        await session.flush()

        for role in user.role:
            user_role_map = UserRoleMapEntity(
                **UserRoleMapBase(id_user=new_user.id,
                                  id_role=role.id,
                                  status=True).dict())
            session.add(user_role_map)

        await session.commit()
        return "User added successfully"

    @async_db_request_handler
    async def get_user(self, pagination: Pagination, session: AsyncSession):
        if not pagination.page or pagination.page < 0:
            pagination.page = env_config.PAGINATION_PAGE

        if not pagination.limit or pagination.limit < 0:
            pagination.limit = env_config.PAGINATION_LIMIT

        query = select(UserEntity).limit(pagination.limit).offset(pagination.page * pagination.limit)
        result = await session.execute(query)
        data = result.scalars().all()

        total_query = select(UserEntity).where(UserEntity.status == 1).with_only_columns(func.count())
        result = await session.execute(total_query)
        total = result.scalar()

        return generate_pagination_response(data,
                                            total,
                                            pagination.page,
                                            pagination.limit,
                                            "/user/get/all/")

    @async_db_request_handler
    async def get_user_by_id(self, user_id: int, session: AsyncSession, func=None, *args, **kwargs):
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")

        query = select(UserEntity).where(UserEntity.id == user_id)
        result = await session.execute(query)

        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(user_id, session, *args, **kwargs)
        return user

    @async_db_request_handler
    async def get_user_by_email(self, email: str, session: AsyncSession, func=None, *args, **kwargs):
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

        query = select(UserEntity).where(UserEntity.email == email)
        result = await session.execute(query)

        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(user.id, session, *args, **kwargs)

        return user

    @async_db_request_handler
    async def update_user(self, user_id: int, session: AsyncSession, user: UserUpdate):
        query = select(UserEntity).where(UserEntity.id == user_id)
        result = await session.execute(query)

        user_full = UserFull(**result.scalars().first().__dict__)
        user_full.updated_date = datetime.now()
        user_full = user_full.copy(update=user.dict(exclude_unset=True))

        query = (update(UserEntity)
                 .where(UserEntity.id == user_id)
                 .values(user_full.dict()))
        await session.execute(query)

        if user.role:
            for role in user.role:
                user_role_map = UserRoleMapEntity(
                    **UserRoleMapBase(id_user=user.id,
                                      id_role=role.id,
                                      status=True).dict())
                session.add(user_role_map)

        await session.commit()

        fullname = f" {user_full.first_name} {user_full.last_name} " \
            if user_full.first_name and user_full.last_name else f" {user_full.email} "

        return f"User{fullname}updated successfully"

    @async_db_request_handler
    async def delete_user(self, user_id: int, session: AsyncSession):
        query = delete(UserEntity).where(UserEntity.id == user_id)
        await session.execute(query)
        await session.commit()
        return "User deleted successfully"

    @async_db_request_handler
    async def activate_user(self, user_id: int, session: AsyncSession):
        query = (update(UserEntity)
                 .where(UserEntity.id == user_id)
                 .values(status=True))
        await session.execute(query)
        await session.commit()
        return "User activated successfully"

    @async_db_request_handler
    async def deactivate_user(self, user_id: int, session: AsyncSession):
        query = (update(UserEntity)
                 .where(UserEntity.id == user_id)
                 .values(status=False))
        await session.execute(query)
        await session.commit()
        return "User deactivated successfully"

    @async_db_request_handler
    async def update_password(self, user_id: int, session: AsyncSession, update_user: UserUpdatePassword):
        query = select(UserEntity).where(UserEntity.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        if not verify(update_user.old_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")

        validate_password(update_user.password)

        query = (update(UserEntity)
                 .where(UserEntity.id == user_id)
                 .values(password=hash_password(update_user.password)))
        await session.execute(query)
        await session.commit()
        return "Password updated successfully"

    @async_db_request_handler
    async def reset_password(self, user_id: int, session: AsyncSession):
        random_str = string.ascii_letters + string.digits + string.punctuation

        while True:
            try:
                new_password = ''.join(random.choices(random_str, k=20))
                validate_password(new_password)
                break
            except Exception as e:
                pass

        query = (update(UserEntity)
                 .where(UserEntity.id == user_id)
                 .values(password=hash_password(new_password)))
        await session.execute(query)
        await session.commit()
        return new_password

    @async_db_request_handler
    async def get_user_roles(self, user_id: int, session: AsyncSession):
        query = select(UserRoleMapEntity.id_role).where(UserRoleMapEntity.id_user == user_id)
        result = await session.execute(query)
        return result.scalars().all()

