# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text

# import api.domain.deviceGroup.models as deviceGroup_models
# import api.domain.deviceList.models as deviceList_models
# import api.domain.project.models as project_models
# import api.domain.template.models as template_models
# import api.domain.user.models as user_models
# import model.models as models
from async_db.wrapper import async_db_request_handler
# from database.db import get_db
from database.sql.device import all_query
from utils.mqttManager import mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_all_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)
class ProjectService:
    def __init__(self, command=""):
        self.command=command
    async def init_pm2(self):
        await restart_all_program_pm2()
    async def init_logging_rate(self):
        pm2_app_list=[f'LogFile|',f'LogDevice|']
        await restart_program_pm2_many(pm2_app_list)
    @staticmethod
    @async_db_request_handler
    async def project_inform(session: AsyncSession):
        try:
            query ="SELECT * FROM `project_setup`"
            result = await session.execute(text(query))
            project = [row._asdict() for row in result.all()][0]
        except Exception as e:
            print("Error create_dev_rs485: ", e)
        finally:
            print('create_dev_rs485 end')
            await session.close()
            return project