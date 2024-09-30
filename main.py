import asyncio
import os
import sys
from src.device_manager.device_manager_service import DeviceManagerService
# path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
# sys.path.append(path)
sys.stdout.reconfigure(encoding='utf-8')
from src.configs.config import Config
from src.configs.config import orm_provider as db_config
from src.mqtt_client.mqtt_client_model import MQTTConfigBase
from src.utils.project_setup.project_setup_service import ProjectSetupService
from src.utils.project_setup.project_setup_model import ProjectSetup
from src.utils.point_list_type.point_list_type_model import PointListTypes
from src.utils.point_list_type.point_list_type_service import PointListTypeService



async def main():
    tasks = []
    MQTT_BROKER = Config.MQTT_BROKER
    MQTT_PORT = Config.MQTT_PORT
    MQTT_USERNAME = Config.MQTT_USERNAME
    MQTT_PASSWORD =Config.MQTT_PASSWORD

    
    db_new=await db_config.get_db()
    project_setup: ProjectSetup =await ProjectSetupService.get_project_setup(db_new)
    if not project_setup:
        print('Error table project_setup')
        return 
    
    mqtt_config=MQTTConfigBase(host=MQTT_BROKER,port=MQTT_PORT,username=MQTT_USERNAME,password=MQTT_PASSWORD,serial_number=project_setup.serial_number)
    
    api_gateway=DeviceManagerService(db_new,project_setup,mqtt_config)
    
    await api_gateway.init()
    
    tasks.append(asyncio.create_task(
        api_gateway.device_manager()))
    await asyncio.gather(*tasks, return_exceptions=False)

    
if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    finally:
        pass
    
