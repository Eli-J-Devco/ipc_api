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
from api.domain.sld_group.sld_group_model import (SldGroupBase,
                                                  SldGroupResponse,
                                                  SldGroupUpdate)
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
    async def get_all_group(self, code,payload,
                            session: AsyncSession):
        try: 
            query =select(SldGroupEntity.id,SldGroupEntity.name,SldGroupEntity.type).where(SldGroupEntity.status == 111)
            result = await session.execute(query)
            sld_group=[row._asdict() for row in  result.all()]
            await session.commit()
            status= 200
        except Exception as e:
            print("Error get_all_group: ", e)
            status= 500
        finally:
            await session.close()
            return SldGroupResponse(code=code, status= status, payload={})
    @async_db_request_handler
    async def add_group(self, code,payload:SldGroupBase,
                            session: AsyncSession):
        try:
            # query =select(SldGroupEntity.id,SldGroupEntity.name).where(SldGroupEntity.status == 1)
            # print(query)
            # result = await session.execute(query)
            # sld_group=[row._asdict() for row in  result.all()]
            # print(sld_group)
            new_sld_group=SldGroupEntity(**payload.dict()) #exclude={"name"}
            # new_sld_group=SldGroupEntity(**SldGroupBase(**payload).dict()) #exclude={"name"}
            session.add(new_sld_group)
            await session.flush()
            await session.commit()
            # insert
            # new_sld_group=SldGroupEntity(name="Group 55",type=0, status=1)
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
            status= 200
        except Exception as e:
            print("Error add_group: ", e)
            status= 500
            return SldGroupResponse(code=code, status= 500, payload=[])
        finally:
            await session.close()
            return SldGroupResponse(code=code, status= status, 
                                    payload=new_sld_group.__dict__)
    @async_db_request_handler
    async def update_group(self, code,payload:SldGroupUpdate,
                                session: AsyncSession):
        try: 
            query = (update(SldGroupEntity)
                    .where(SldGroupEntity.id == payload.id)
                    .values(name=payload.name,type=payload.type))
            await session.execute(query)
            await session.commit()
            
        except Exception as e:
            print("Error update_group: ", e)
            return SldGroupResponse(code=code, status= 500, payload={})
        finally:
            await session.close()
            return SldGroupResponse(code=code, status= 200, payload={})
    @async_db_request_handler
    async def delete_group(self, code,payload:SldGroupUpdate,
                                session: AsyncSession):
        try: 
            query =delete(SldGroupEntity).where(SldGroupEntity.id == payload.id)
            result = await session.execute(query)
            await session.commit()
            status= 200
        except Exception as e:
            print("Error delete_group: ", e)
            status= 500
        finally:
            await session.close()
            return SldGroupResponse(code=code, status= status, payload={})
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