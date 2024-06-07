# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import (delete, func, insert, join, literal_column, select,
                            text, update)

import api.domain.sld_group.sld_group_entity as user_models
from api.domain.sld_group.sld_group_entity import SldGroup as SldGroupEntity
from api.domain.sld_group.sld_group_model import SldGroupBase
# from api.domain.sld_group.sld_group_entity import SldGroupInv as SldGroupEntity
from async_db.wrapper import async_db_request_handler
from configs.config import orm_provider as db_config
# import api.domain.deviceGroup.models as deviceGroup_models
# import api.domain.deviceList.models as deviceList_models
# import api.domain.project.models as project_models
# import api.domain.template.models as template_models
# import api.domain.user.models as user_models
# import model.models as models
# from database.db import get_db
from database.sql.single_line_diagram import all_query
from utils.mqttManager import mqtt_public, mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_all_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)


class SLDService:
    def __init__(self, sld=""):
        self.sld=sld
    @async_db_request_handler
    async def add_group(self, payload,session: AsyncSession):
        try:
            # query =select(SldGroupEntity.id,SldGroupEntity.name).where(SldGroupEntity.status == 1)
            # print(query)
            # result = await session.execute(query)
            # sld_group=[row._asdict() for row in  result.all()]
            # print(sld_group)
            data={
                # "id":1,
                "name":"Group 1",
                "type":0,
                "status":True
            }
            # new_sld_group=SldGroupEntity(**SldGroupBase(**data).dict(exclude={"name"}))
            # print(new_sld_group)
            # session.add(new_sld_group)
            # await session.flush()
            # await session.commit()
            # insert
            # new_sld_group=SldGroupEntity(name="Group 55",type=0, status=1)
            # print(new_sld_group)
            # session.add(new_sld_group)
            # await session.flush()
            # await session.commit()
            
            # Delete
            # query =delete(SldGroupEntity).where(SldGroupEntity.id == 15)
            # print(query)
            # result = await session.execute(query)
            # await session.commit()
            
            # Update 
            # query = (update(SldGroupEntity)
            #      .where(SldGroupEntity.id == 11)
            #      .values(name="hi",type=1))
            # await session.execute(query)
            # await session.commit()
            # query = (update(SldGroupEntity)
            #      .where(SldGroupEntity.id == register_block.id)
            #      .values(SldGroupEntity.dict(exclude_unset=True)))
            
            # sql_add_group=all_query.add_sld_group.format(name=payload["name"],group_type=payload["type"] )
            # result= await session.execute(text(sql_add_group))
            # await session.commit()
        except Exception as e:
            print("Error add_group: ", e)
        finally:
            print('add_group end')
            await session.close()
    # @async_db_request_handler
    # async def delete_group(self, payload,session: AsyncSession):
    #     try:
    #         sql_add_group=all_query.add_sld_group.format(name=payload["name"],group_type=payload["type"] )
    #         result= await session.execute(text(sql_add_group))
    #         await session.commit()
    #     except Exception as e:
    #         print("Error add_group: ", e)
    #     finally:
    #         print('add_group end')
    #         await session.close()
    # @async_db_request_handler
    # async def add_group_inv(self, payload,session: AsyncSession):
    #     try:
    #         sql_add_group=all_query.add_sld_group.format(id_sld_group=payload["id_sld_group"],group_type=payload["type"] )
    #         result= await session.execute(text(sql_add_group))
    #         await session.commit()
    #     except Exception as e:
    #         print("Error add_group: ", e)
    #     finally:
    #         print('add_group end')
    #         await session.close()
    # @async_db_request_handler
    # async def add_group_meter(self, payload,session: AsyncSession):