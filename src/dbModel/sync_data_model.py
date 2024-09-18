from pydantic import BaseModel
from datetime import datetime

class SyncDataModel(BaseModel):
    id: int
    id_device: int
    modbusdevice: str
    ensuredir: str
    source: str
    filename: str
    createtime: datetime
    data: str
    id_upload_channel: int
    synced: int
    updatetime: datetime = None
    error: int = None
    number_of_time_retry: int = 0

    class Config:
        orm_mode = True