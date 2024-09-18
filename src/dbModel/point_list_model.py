from pydantic import BaseModel

class PointKeyModel(BaseModel):
    id_pointkey: int
    namekey: str

    class Config:
        orm_mode = True