from typing import Optional
from pydantic import BaseModel


class ConfigInformationGroup(BaseModel):
    MIN: int
    MAX: int


class ConfigInformationEnum:
    TYPE_DATATYPE = ConfigInformationGroup(MIN=1, MAX=14)
    TYPE_BYTEORDER = ConfigInformationGroup(MIN=15, MAX=22)
    TYPE_UNIT = ConfigInformationGroup(MIN=23, MAX=134)
    TYPE_BAUD_RATE = ConfigInformationGroup(MIN=135, MAX=140)
    TYPE_PARITY = ConfigInformationGroup(MIN=141, MAX=145)
    TYPE_STOP_BIT = ConfigInformationGroup(MIN=146, MAX=149)
    TYPE_MODBUS_DEBUG_LEVEL = ConfigInformationGroup(MIN=150, MAX=154)
    TYPE_MODBUS_TIMEOUT = ConfigInformationGroup(MIN=155, MAX=164)
    TYPE_MODBUS_FUNCTION = ConfigInformationGroup(MIN=165, MAX=170)
    TYPE_LOGGING_INTERVAL = ConfigInformationGroup(MIN=171, MAX=182)
    TYPE_UPDATE_PROTOCOL = ConfigInformationGroup(MIN=183, MAX=189)
    TYPE_NETWORK_ACCESS = ConfigInformationGroup(MIN=190, MAX=194)
    TYPE_TIME_WAIT_BEFORE_RETRY = ConfigInformationGroup(MIN=195, MAX=212)
    TYPE_UPLOAD_DEBUG_INFORMATION = ConfigInformationGroup(MIN=213, MAX=217)
    TYPE_SCHEDULED_UPLOAD_TIME = ConfigInformationGroup(MIN=218, MAX=247)
    TYPE_ETHERNET = ConfigInformationGroup(MIN=248, MAX=252)
    TYPE_POINT = ConfigInformationGroup(MIN=262, MAX=264)
    TYPE_MODBUS_CUSTOM = ConfigInformationGroup(MIN=265, MAX=269)
    TYPE_CREATE_TEMPLATE = ConfigInformationGroup(MIN=270, MAX=272)
    TYPE_MPPT = ConfigInformationGroup(MIN=273, MAX=279)


class ProjectBaseFilter(BaseModel):
    id: int


class UpdateProjectSetupFilter(ProjectBaseFilter):
    name: str
    serial_number: str
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None


class UpdateLoggingIntervalFilter(ProjectBaseFilter):
    id_logging_interval: int


class UpdateProjectFilter(ProjectBaseFilter):
    name: str
    serial_number: str
    mode: int
    location: str
    description: str
    administrative_contact: str


class UpdateFirstPageLoginFilter(ProjectBaseFilter):
    id_first_page_on_login: int


class UpdateRemoteAccessFilter(ProjectBaseFilter):
    link_remote_access: str
    allow_remote_access: bool


class UpdateSearchRTUFilter(ProjectBaseFilter):
    enable_search_modbus_rtu_device: bool
