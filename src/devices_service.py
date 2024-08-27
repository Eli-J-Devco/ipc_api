import logging

from mqtt_service.mqtt import Publisher
from mqtt_service.model import MessageModel, Topic
from sqlalchemy import Double
from sqlalchemy.ext.asyncio import AsyncSession

from .create_table_module.create_table_service import TableColumn, CreateTableService
from .delete_table_module.delete_table_service import DeleteTableService
from .devices_model import DeviceModel, Action, DeviceState
from .pm2_service.model import MessageModel as PM2MessageModel, PayloadModel, DeviceModel as PM2DeviceModel
from .pm2_service.pm2_service import PM2Service
from .update_table_module.update_table_service import UpdateTableService

logger = logging.getLogger(__name__)


class DeviceService:
    def __init__(self,
                 session: AsyncSession,
                 create_table_service: CreateTableService,
                 update_table_service: UpdateTableService,
                 delete_table_service: DeleteTableService,
                 retry_publisher: Publisher,
                 dead_letter_publisher: Publisher,
                 serial_number: str,
                 handle_error,
                 pm2_service: PM2Service):
        self.session = session
        self.create_table_service = create_table_service
        self.update_table_service = update_table_service
        self.delete_table_service = delete_table_service
        self.retry_publisher = retry_publisher
        self.dead_letter_publisher = dead_letter_publisher
        self.serial_number = serial_number
        self.handle_error = handle_error
        self.pm2_service = pm2_service
        self.action = {
            Action.CREATE.value: self.create_table,
            Action.UPDATE.value: self.update_table,
            Action.DELETE.value: self.delete_table
        }

    async def handler(self, data: MessageModel):
        devices = data.message.get("devices")
        action_type = data.message.get("type")
        code = data.message.get("code")
        retry = data.metadata.retry
        meta_code = data.metadata.code

        try:
            devices_info = await self.get_valid_devices(devices, action_type)

            if not devices_info:
                return

            logger.info("Processing devices")
            result = {}
            send_device = []
            for device in devices_info:
                result[device.id] = await self.action[action_type](device, retry, code, meta_code)
                msg = PM2DeviceModel(id=device.id,
                                     name=device.name,
                                     id_communication=device.communication.id
                                     if device.communication else None,
                                     connect_type=device.communication.name
                                     if device.communication else None,
                                     mode=0,
                                     device_type_value=device.device_type.type, )
                if result[device.id] == 200:
                    send_device.append(msg)
                elif isinstance(result[device.id], list):
                    send_device.append(msg)
                    send_device.extend(result[device.id])

            if len(send_device) > 0:
                if action_type != Action.UPDATE.value:
                    pm2_msg = PM2MessageModel(CODE=code,
                                              PAYLOAD=PayloadModel(
                                                  id_communication=send_device[0].id_communication,
                                                  device=send_device,
                                                  delete_mode=2 if action_type == Action.DELETE.value else None))
                else:
                    pm2_msg = PM2MessageModel(CODE=code,
                                              PAYLOAD=PayloadModel(id=devices_info[0].id_template, ))
                await self.pm2_service.send(pm2_msg)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            await self.session.rollback()
            raise e

    async def get_valid_devices(self, devices, action_type):
        all_devices = await self.create_table_service.get_devices(self.session)
        id_templates = {}
        devices_info = []
        for device in all_devices:
            if device.id in devices:
                if action_type != Action.DELETE.value:
                    if device.id_template not in id_templates:
                        id_templates[device.id_template] = (await (self.create_table_service
                                                                   .get_points(device.id_template,
                                                                               self.session)))
                    device.points = id_templates[device.id_template]
                devices_info.append(device)

        if not devices_info:
            logger.error("No devices found")
            return None
        return devices_info

    async def create_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            logger.info(f"Creating table for device: {device.table_name}")
            result = await self.create_table_service.create_table(device.table_name,
                                                                  list(map(lambda x: TableColumn(x.id_pointkey,
                                                                                                 Double),
                                                                           device.points)),
                                                                  self.session)
            if isinstance(result, Exception):
                raise result

            logger.info(f"Adding device mppt for device: {device.table_name}")
            result = await self.create_table_service.add_device_mppt(device, self.session)
            if isinstance(result, Exception):
                raise result

            logger.info(f"Adding device point map for device: {device.table_name}")
            result = await self.create_table_service.add_device_point_list_map(device, self.session)
            if isinstance(result, Exception):
                raise result

            return 200
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.CREATE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.CREATE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher,
                                    is_zip=True)
            if retry == 0:
                await self.update_table_service.update_device_status(device.id,
                                                                     DeviceState.Error.value,
                                                                     self.session)

    async def update_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            logger.info(f"Updating table for device: {device.table_name}")
            result = await self.update_table_service.update_table(device,
                                                                  self.session)

            if isinstance(result, Exception):
                raise result
            logger.info(f"Updated device mppt for device: {device.table_name}")

            return 200
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.UPDATE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.UPDATE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher,
                                    is_zip=True)

    async def delete_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            output = []
            if device.device_type.type == 0:
                logger.info(f"Deleting table for device: {device.table_name}")
                result = await self.delete_table_service.delete_table(device.table_name, self.session)
                if isinstance(result, Exception):
                    raise result

                logger.info(f"Deleting device mppt for device: {device.table_name}")
                result = await self.delete_table_service.delete_device_mppt(device, self.session)
                if isinstance(result, Exception):
                    raise result

                logger.info(f"Deleting device point list map for device: {device.table_name}")
                result = await self.delete_table_service.delete_device_point_list_map(device, self.session)
                if isinstance(result, Exception):
                    raise result

                logger.info(f"Deleting device component for device: {device.table_name}")
                result = await self.delete_table_service.delete_device_component(device.id, self.session)
                if isinstance(result, Exception):
                    raise result
                if isinstance(result, list):
                    output.extend(result)

            logger.info(f"Deleting device")
            result = await self.delete_table_service.delete_device(device.id, self.session)
            if isinstance(result, Exception):
                raise result

            return 200 if len(output) == 0 else output
        except Exception as e:
            logger.error(f"Error deleting table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.DELETE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.DELETE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher,
                                    is_zip=True)
