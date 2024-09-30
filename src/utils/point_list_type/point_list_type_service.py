from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler

from src.utils.point_list_type.point_list_type_entity import  PointListType as PointListTypeEntity
from src.utils.point_list_type.point_list_type_model import  PointListType as PointListTypeModel
from src.utils.point_list_type.point_list_type_model import  PointListTypes as PointListTypesModel

class PointListTypeService:
    @async_db_request_handler
    async def get_point_list_type(session: AsyncSession):
        try:
            query = (select(PointListTypeEntity)
                .where(PointListTypeEntity.status==1)
                )
            result = await session.execute(query)
            point_list_type = result.scalars().all()
            point_types=[]
            for point_type in point_list_type:
                point_types.append(PointListTypeModel(**point_type.__dict__))
        except Exception as e:
            print("Error get_point_list_type: ", e)
            return [] 
        finally:
            await session.close()
            return PointListTypesModel(point_types)  