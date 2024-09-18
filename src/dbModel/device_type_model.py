from pydantic import BaseModel

class DeviceTypeModel(BaseModel):
    name: str

    class Config:
        orm_mode = True