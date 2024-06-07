# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import random
import string
from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from nest.core import Injectable, Depends
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .authentication_model import Authentication, AuthenticationResponse
from .authentication_repository import AuthenticationRepository
from ..config import config
from ..project_setup.project_setup_service import ProjectSetupService
from ..role.role_service import RoleService
from ..user.user_entity import User
from ..user.user_service import UserService
from ..utils.password_hasher import hash_password
from ..utils.utils import validate_password


@Injectable
class AuthenticationService:
    __authentication__ = None

    def __init__(self):
        self.authentication = AuthenticationRepository().get_authentication_config()

    @async_db_request_handler
    async def login(self, user_credential: OAuth2PasswordRequestForm, session: AsyncSession) -> AuthenticationResponse | HTTPException:
        """
        Login user with username and password and return access token and refresh token
        :author: nhan.tran
        :date: 20-05-2024
        :param user_credential:
        :param session:
        :return: AuthenticationResponse | HTTPException
        """
        if not user_credential.username or not user_credential.password:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

        user_provider = Authentication(username=user_credential.username, password=user_credential.password)
        decrypted_user_credential = self.authentication.decrypt_user_credential(user_provider)

        if isinstance(decrypted_user_credential, HTTPException):
            return decrypted_user_credential

        if not decrypted_user_credential.username or not decrypted_user_credential.password:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

        query = select(User).where(User.email == decrypted_user_credential.username)
        result = await session.execute(query)

        if result is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user = result.scalars().first()
        if not (self.authentication
                .verify_password(decrypted_user_credential.password, user.password)):
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

        if not user.status == 1:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

        roles = await UserService(RoleService()).get_user_roles(user.id, session)
        permissions = []
        for role in roles:
            screens = await RoleService().get_role_permissions(role, session)
            permissions.extend(screens)

        access_token = self.authentication.create_access_token(data={"user_id": user.id})
        refresh_token = self.authentication.create_refresh_token(data={"user_id": user.id})
        project_id = await ProjectSetupService().get_project_setup_id(session)

        response = AuthenticationResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            refresh_token=refresh_token,
            access_token=access_token,
            project_id=project_id,
            permissions=permissions
        )

        return response

    @async_db_request_handler
    async def refresh(self, refresh_token: str) -> JSONResponse | HTTPException:
        """
        Refresh the access token with the refresh token
        :author: nhan.tran
        :date: 20-05-2024
        :param refresh_token:
        :return: JSONResponse | HTTPException
        """
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        access_token = self.authentication.refresh_access_token(refresh_token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token})

    @async_db_request_handler
    async def get_current_user(self, session: AsyncSession = Depends(config.get_db),
                               token: str = Depends(AuthenticationRepository()
                                                    .get_authentication_config()
                                                    .get_oauth2_scheme())) -> User | Any:
        """
        Get the current user from the token
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param token:
        :return: User | Any
        """
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail=f"Could not validate credentials",
                                              headers={"WWW-Authenticate": "Bearer"})

        token = self.authentication.verify_access_token(token, credentials_exception)
        user = await session.get(User, token.get("user_id"))
        return user

    @async_db_request_handler
    async def forgot_password(self, email: str, session: AsyncSession) -> JSONResponse | HTTPException:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalars().first()
        if user is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        random_str = string.ascii_letters + string.digits + string.punctuation
        while True:
            try:
                new_password = ''.join(random.choices(random_str, k=20))
                validate_password(new_password)
                break
            except Exception as e:
                pass

        query = (update(User)
                 .where(User.email == email)
                 .values(password=hash_password(new_password)))
        await session.execute(query)
        await session.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "message": "Password has been reset.",
            "new_password": new_password
        })
