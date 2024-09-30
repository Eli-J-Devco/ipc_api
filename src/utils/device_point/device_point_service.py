from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler

from src.utils.device_point.device_point_model import  (DevicePointBase,DevicePointsOutput,
                                                        ControlPointBase,
                                                        ControlPoints

                                                        )
from src.configs.query_sql.point_list import query_all as point_query


class DevicePointService:
    def __init__(self,session: AsyncSession, **kwargs
                    ):
        self.session=session
    @async_db_request_handler
    async def get_device_points(self, id_device: int):
        try:
            device_point_list=[]
            query =point_query.select_point_list.format(id_device=id_device)
            result = await self.session.execute(text(query))
            device_points = [row._asdict() for row in result.all()]
            # print(f'device_points: {device_points}')
            if not device_points:
                return []
            for device_point in device_points:
                device_point_list.append(DevicePointBase(**device_point))
        except Exception as e:
            print("Error get_device_points: ", e)
            return [] 
        finally:
            await self.session.close()
            return DevicePointsOutput(points=device_point_list)
    async def get_device_point_control(self, points: DevicePointsOutput):
        point_list=[]
        try:
            if not points.points:
                return []
            for point in points.points:
                # print(point)
                point_list.append(ControlPointBase(**point.dict()))
        except Exception as e:
            print("Error get_device_point_control: ", e)
            return [] 
        finally:
            pass
        return ControlPoints(point_list)