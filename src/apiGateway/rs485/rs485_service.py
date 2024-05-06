# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.sql import func, insert, join, literal_column, select, text

import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.project.models as project_models
import api.domain.template.models as template_models
import api.domain.user.models as user_models
import model.models as models
from database.db import get_db
from database.sql.rs485 import all_query
from utils.mqttManager import mqtt_public, mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_all_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)


class RS485Service:
    def __init__(self, command=""):
        self.command=command
    async def init_pm2(self, communication):
        try:
            
            db=get_db()
            id_communication=communication["id"]
            sql_query_select_device=all_query.select_all_device_communication.format(id_communication=id_communication)
            result_device = db.execute(text(sql_query_select_device)).all()
            results_device_dict = [row._asdict() for row in result_device]
            if results_device_dict:
                pm2_app_list=[f'Dev|{id_communication}']
                await restart_program_pm2_many(pm2_app_list)
            db.close()
        
        except Exception as e:
            print("Error RS485 init_pm2: ", e)