import asyncio
import enum
import logging
import pathlib
from functools import reduce
import requests
from sqlalchemy import Double

from ..src.create_devices_model import DeviceModel
from ..logger.logger import setup_logging
from ..src.utils.password_hasher import AccountHasher
from ..src.config import config
from ..src.create_table_module.create_table_service import CreateTableService, TableColumn
from ..src.config import orm_provider as db_config

setup_logging(log_path=f"{pathlib.Path(__file__).parent.absolute()}\\log")


async def run_tasks(tasks: list[asyncio.Task]):
    await asyncio.gather(*tasks)


async def create_table(device: DeviceModel, create_table_service: CreateTableService):
    logging.info(f"Creating table for device: {device.table_name}")
    await create_table_service.create_table(device.table_name,
                                            list(map(lambda x: TableColumn(x.id_pointkey,
                                                                           Double),
                                                     device.points)),
                                            await db_config.get_db())


async def delete_table(device: DeviceModel, create_table_service: CreateTableService):
    logging.info(f"Deleting table for device: {device.table_name}")
    await create_table_service.delete_table(device.table_name, await db_config.get_db())


class Action(enum.Enum):
    CREATE = "devices/create"
    DELETE = "devices/delete"
    DEAD_LETTER = "devices/dead-letter"


action = {
    Action.CREATE.value: create_table,
    Action.DELETE.value: delete_table
}


def get_devices(devices, action_type):
    try:
        create_table_service = CreateTableService(db_config.Base.metadata)
        all_devices = asyncio.run(create_table_service.get_devices(asyncio.run(db_config.get_db())))
        logging.info(f"Devices: {all_devices}")
        devices_info = []
        id_templates = {}
        for device in all_devices:
            if device.id in devices:
                if device.id_template not in id_templates:
                    id_templates[device.id_template] = (asyncio
                                                        .run(create_table_service
                                                             .get_points(device.id_template,
                                                                         asyncio.run(db_config.get_db()))))
                logging.info(f"Points: {id_templates[device.id_template]}")
                device.points = id_templates[device.id_template]
                devices_info.append(device)

        try:
            event_loop = asyncio.get_event_loop()
        except RuntimeError:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

        tasks = []
        for device in devices_info:
            tasks.append(event_loop.create_task(action[action_type](device, create_table_service)))

        event_loop.run_until_complete(run_tasks(tasks))
    except Exception as e:
        logging.error(f"Error creating table: {e}")


if __name__ == "__main__":
    # event_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(event_loop)
    # tasks = [event_loop.create_task(get_devices(i)) for i in range(657, 659)]
    # event_loop.run_until_complete(asyncio.gather(*tasks))
    # event_loop.close()
    get_devices([554], Action.DELETE.value)
