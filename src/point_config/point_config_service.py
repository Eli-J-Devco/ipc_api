from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler

from .point_config_filter import PointTypeNames, PointType
from .point_control_group_config_service import PointControlGroupConfigService


@Injectable
class PointConfigService(PointControlGroupConfigService):
    @async_db_request_handler
    async def get_point_type(self):
        names = PointTypeNames().dict().values()
        return [{
            "id": PointType().__getattribute__(name),
            "name": name
        } for name in names]
