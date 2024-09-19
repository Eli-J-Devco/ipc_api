from pydantic import BaseModel

class PointKeyModel(BaseModel):
    id_pointkey: str
    namekey: str

    class Config:
        orm_mode = True