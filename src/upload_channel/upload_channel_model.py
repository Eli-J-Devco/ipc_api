from typing import Optional

from pydantic import BaseModel

from ..devices.devices_model import DeviceUploadChannelMap
from ..project_setup.project_setup_model import ConfigInformationShort


class UploadChannel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    id_type_protocol: Optional[int] = None
    id_type_logging_interval: Optional[int] = None
    uploadurl: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    selected_upload: Optional[str] = None
    enable: Optional[bool] = None
    allow_remote_configuration: Optional[bool] = None
    status: Optional[bool] = None


class UploadChannelDeviceMap(BaseModel):
    id_upload_channel: int
    id_device: int

    class Config:
        orm_mode = True


class UploadChannelConfig(UploadChannel):
    type_protocol: Optional[ConfigInformationShort] = None
    logging_interval: Optional[ConfigInformationShort] = None
    devices: Optional[list[DeviceUploadChannelMap]] = None

    class Config:
        orm_mode = True


class UploadChannelConfigs(BaseModel):
    type_protocols: list[ConfigInformationShort] = []
    logging_intervals: list[ConfigInformationShort] = []
    devices: Optional[list[DeviceUploadChannelMap]] = []