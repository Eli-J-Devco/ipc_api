# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .authentication_controller import AuthenticationController
from .authentication_service import AuthenticationService
from .authentication_model import AuthenticationConfig
from ..config import env_config


@Module(
    controllers=[AuthenticationController],
    providers=[AuthenticationService],
    imports=[]
)   
class AuthenticationModule:
    auth = AuthenticationConfig(password_secret_key=env_config.PASSWORD_SECRET_KEY)
    