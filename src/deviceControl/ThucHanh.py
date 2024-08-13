# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import base64
import collections
import datetime
import gzip
import json
import logging
import os
import platform
import sys
from datetime import datetime

import mqttools
import psutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *
import cpu.cpu_service as cpu_init
import control.control_service as control_init
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                                mqtt_public_paho, mqtt_public_paho_zip,
                                mqttService)
from configs.config import orm_provider as db_config
from database.sql.device import all_query
from dataclasses import asdict, dataclass

from apiGateway.devices import devices_service
from apiGateway.project_setup import project_service
from apiGateway.rs485 import rs485_service
from apiGateway.template import template_service
from apiGateway.upload_channel import upload_channel_service

async def main():
    # Map Library 
    project_init=project_service.ProjectService()
    template_init=template_service.TemplateService()
    upload_channel_init=upload_channel_service.UploadChannelService()
    rs485_init=rs485_service.RS485Service()
            # 
# ======================================= SELECT =======================================================
# ======== project_setup ============
    db_new=await db_config.get_db() # Khoi Tao Thong So Ket Noi DB
    print("db_new",db_new)
    results_project=await project_init.project_inform(db_new) # 
    print("Result From Project Setup",results_project)
    
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())