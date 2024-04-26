from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from .authentication_model import Authentication, AuthenticationResponse
from .authentication_repository import AuthenticationRepository

from ..config import config
from ..project_setup.project_setup_service import ProjectSetupService

from ..user.user_entity import User
from ..user.user_service import UserService
from ..role.role_service import RoleService

@Injectable
class AuthenticationService:
    __authentication__ = None

    def __init__(self):
        self.authentication = AuthenticationRepository().get_authentication_config()

    @async_db_request_handler
    async def login(self, user_credential: OAuth2PasswordRequestForm, session: AsyncSession):
        if not user_credential.username or not user_credential.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

        user_provider = Authentication(username=user_credential.username, password=user_credential.password)
        decrypted_user_credential = self.authentication.decrypt_user_credential(user_provider)
        query = select(User).where(User.email == decrypted_user_credential.username)
        result = await session.execute(query)

        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user = result.scalars().first()
        if not (self.authentication
                .verify_password(decrypted_user_credential.password, user.password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

        if not user.status == 1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

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
    async def refresh(self, refresh_token: str):
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        access_token = self.authentication.refresh_access_token(refresh_token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token})

    @async_db_request_handler
    async def get_current_user(self, session: AsyncSession = Depends(config.get_db),
                               token: str = Depends(AuthenticationRepository()
                                                    .get_authentication_config()
                                                    .get_oauth2_scheme())):

        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail=f"Could not validate credentials",
                                              headers={"WWW-Authenticate": "Bearer"})

        token = self.authentication.get_authentication_config().verify_access_token(token, credentials_exception)
        user = await session.get(User, token.get("user_id"))
        return user
