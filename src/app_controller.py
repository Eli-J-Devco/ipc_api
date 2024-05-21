# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Controller, Get
from .app_service import AppService


@Controller("/")
class AppController:

    def __init__(self, service: AppService):
        self.service = service

    @Get("/")
    def get_app_info(self):
        return self.service.get_app_info()