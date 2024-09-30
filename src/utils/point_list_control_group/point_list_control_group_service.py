from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler

from src.utils.point_list_control_group.point_list_control_group_model import  PointListControlGroup,PointListControlGroupsOut
from src.configs.query_sql.point_list import query_all as point_query


class PointListControlGroupService:
    def __init__(self,session: AsyncSession, **kwargs):
        self.session=session
    @async_db_request_handler
    async def get_point_list_control_groups(self, id_template: int):
        try:
            control_group_list=[]
            query =point_query.select_point_list_control_group.format(id_template=id_template)
            result = await self.session.execute(text(query))
            control_groups = [row._asdict() for row in result.all()]
            if not control_groups:
                return []
            for control_group in control_groups:
                control_group_list.append(PointListControlGroup(**control_group))
        except Exception as e:
            print("Error get_point_list_control_groups: ", e)
            return [] 
        finally:
            await self.session.close()
            return PointListControlGroupsOut(control_group_list)  
 