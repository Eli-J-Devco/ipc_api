from nest.core import Injectable, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from .authentication_model import AuthenticationConfig

from ..config import env_config, config
from ..user.user_entity import User


@Injectable
class AuthenticationRepository:
    __authentication_config__ = None

    @staticmethod
    def get_authentication_config():
        if AuthenticationRepository.__authentication_config__ is None:
            AuthenticationRepository.__authentication_config__ = AuthenticationConfig(
                password_secret_key=env_config.PASSWORD_SECRET_KEY,
            )
        return AuthenticationRepository.__authentication_config__


async def get_current_user(session: AsyncSession = Depends(config.get_db),
                           token: str = Depends(
                               AuthenticationRepository.get_authentication_config().get_oauth2_scheme())):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = AuthenticationRepository.get_authentication_config().verify_access_token(token, credentials_exception)
    user = await session.get(User, token.id)
    return user
