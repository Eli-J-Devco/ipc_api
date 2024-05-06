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
from database.sql.template import all_query
from utils.mqttManager import mqtt_public, mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_all_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)


class TemplateService:
    def __init__(self, command=""):
        self.command=command
    async def init_pm2(self, template):
        # restart Dev
        # restart LogDevice
        # restart LogFile ****
        # pm2_app_list=[f'LogFile|',f'LogDevice|']
        # await restart_program_pm2_many(pm2_app_list)
        db=get_db()
        print(template)
        id_template=template['id']
        sql_query_select_device=all_query.select_device_through_template.format(id_template=id_template)
        result_device = db.execute(text(sql_query_select_device)).all()
        db.close()
        device_tcp=[]
        device_rs485=[]
        communication_list=[]
        if result_device:
            results_device_dict = [row._asdict() for row in result_device]
            for item in results_device_dict:
                if item["connect_type"]=="RS485":
                    communication_list.append(item['id_communication'])
                elif item["connect_type"]=="Modbus/TCP":
                    device_tcp.append(f'Dev|{item["id_communication"]}|Modbus/TCP|{item["id"]}')
                else:
                    pass
        if device_tcp:
            await restart_program_pm2_many(device_tcp)
        if communication_list:
            device_rs485=list(set(communication_list))
            print(f'device_rs485: {device_rs485}')
            pm2_app_list=[]
            for item in device_rs485:
                pid=f'Dev|{item}'
                pm2_app_list.append(pid)
            await restart_program_pm2_many(pm2_app_list)
        if communication_list and device_tcp:
            pm2_app_list=[f'LogFile|',f'LogDevice|']
            await restart_program_pm2_many(pm2_app_list)