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
from database.sql.upload_channel import all_query
from utils.mqttManager import mqtt_public, mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_all_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)


class UploadChannelService:
    def __init__(self, command=""):
        self.command=command
    async def init_pm2(self, upload_channel_list):
        try:
            
            pm2_app_list_delete=[]
            pm2_app_list_create=[]
            pm2_app_list_init=[]
            db=get_db()
            for item in upload_channel_list:
                
                id_upload_channel=item['id']
                sql_query_select_device=all_query.select_upload_channel.format(id_upload_channel=id_upload_channel)
                result_upload_channel = db.execute(text(sql_query_select_device)).all()
                results_upload_channel_dict = [row._asdict() for row in result_upload_channel]
                
                if results_upload_channel_dict:
                    result_channel=results_upload_channel_dict[0]
                    if result_channel["enable"]==1:
                        
                        id=result_channel["id"]
                        name = result_channel["name"]
                        type_protocol= result_channel["type_protocol"]
                        
                        pm2_app_list_create.append({
                            "log_path_file":f'{path}/dataLog/file.py',
                            "pid_log":f'LogFile|{id}|{name}|{type_protocol}',
                            
                            "up_path_file":f'{path}/dataSync/url.py',
                            "pid_up":f'UpData|{id}|{name}|{type_protocol}',
                            "id":result_channel["id"]
                        })
                        pm2_app_list_init.append(f'LogFile|{result_channel["id"]}')
                        pm2_app_list_init.append(f'UpData|{result_channel["id"]}')
                    else:
                        pm2_app_list_delete.append(
                            f'LogFile|{result_channel["id"]}'
                        )
                        pm2_app_list_delete.append(
                            f'UpData|{result_channel["id"]}'
                        )
                    
            db.close()
            if pm2_app_list_init:
                await delete_program_pm2_many(pm2_app_list_init)
            if pm2_app_list_delete:
                await delete_program_pm2_many(pm2_app_list_delete)
            if pm2_app_list_create:
                for item in pm2_app_list_create:
                    await create_program_pm2(item["log_path_file"],item["pid_log"],item["id"])
                for item in pm2_app_list_create:
                    await create_program_pm2(item["up_path_file"],item["pid_up"],item["id"])
                
            # pm2 start D:\NEXTWAVE\project\ipc_api\src\dataLog\file.py -f --name "LogFile|2|Channel 2|XML" -- 2
            # pm2 start D:\NEXTWAVE\project\ipc_api\src\dataSync\url.py -f --name "UpData|2|Channel 2|XML" -- 2
        except Exception as e:
            print("Error UploadChannelService: ", e)