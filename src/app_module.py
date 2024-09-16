# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import logging
from nest.core import PyNestFactory, Module
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from .config import config
from .app_controller import AppController
from .app_service import AppService
from .devices.devices_module import DevicesModule
from .template.template_module import TemplateModule
from .point.point_module import PointModule
from .project_setup.project_setup_module import ProjectSetupModule
from .authentication.authentication_module import AuthenticationModule
from .ethernet.ethernet_module import EthernetModule
from .rs485.rs485_module import Rs485Module
from .user.user_module import UserModule
from .role.role_module import RoleModule
from .upload_channel.upload_channel_module import UploadChannelModule
from .point_config.point_config_module import PointConfigModule
from .point_external.point_external_module import PointMpptModule
from .point_control.point_control_module import PointControlModule
from .register_block.register_block_module import RegisterBlockModule
from .device_point.device_point_module import DevicePointModule


@Module(
    imports=[
        AuthenticationModule,
        DevicesModule,
        EthernetModule,
        PointModule,
        PointConfigModule,
        PointMpptModule,
        PointControlModule,
        ProjectSetupModule,
        RoleModule,
        Rs485Module,
        TemplateModule,
        UploadChannelModule,
        UserModule,
        RegisterBlockModule,
        DevicePointModule,
    ],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="IPC API",
    title="IPC API",
    version="1.0.0",
    debug=True,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)
http_server = app.get_server()
http_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@http_server.get("/docs", include_in_schema=False)
def get_docs(current_user: str = Depends(AppService.get_current_user)):
    return AppService().get_app_docs()


@http_server.get("/redoc", include_in_schema=False)
def get_redoc(current_user: str = Depends(AppService.get_current_user)):
    return AppService().get_app_redoc()


@http_server.get("/openapi.json", include_in_schema=False)
def get_openapi_json(current_user: str = Depends(AppService.get_current_user)):
    return AppService().get_openapi_json(http_server)


@http_server.on_event("startup")
async def startup():
    try:
        await asyncio.wait_for(config.create_all(), timeout=30)
    except asyncio.TimeoutError:
        logging.error("Timeout occurred while creating all tables")
    except Exception as e:
        logging.error(f"Error occurred while creating all tables: {e}")
