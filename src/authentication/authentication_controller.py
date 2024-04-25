from functools import reduce

from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Response, Body
from fastapi.responses import JSONResponse

from .authentication_service import AuthenticationService

from ..config import config
from ..utils.service_wrapper import ServiceWrapper

@Controller("authentication")
class AuthenticationController:

    def __init__(self, authentication_service: AuthenticationService):
        self.authentication_service = authentication_service

    @Post("/login")
    async def login(self,
                    user_credentials: OAuth2PasswordRequestForm = Depends(),
                    session: AsyncSession = Depends(config.get_db)):
        return await ServiceWrapper.async_wrapper(self.authentication_service.login)(user_credentials, session)

    @Post("/logout")
    async def logout(self, response: Response, session: AsyncSession = Depends(config.get_db)):
        response.delete_cookie("refresh_token")
        return JSONResponse(status_code=200, content={"message": "Logout successful"})

    @Post("/refresh")
    async def refresh(self, refresh_token: str = Body(embed=True), session: AsyncSession = Depends(config.get_db)):
        return await ServiceWrapper.async_wrapper(self.authentication_service.refresh)(refresh_token)
