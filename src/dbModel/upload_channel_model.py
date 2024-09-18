from pydantic import BaseModel

class UploadChannelModel(BaseModel):
    id: int
    uploadurl: str
    status: int
    id_type_protocol: int

    class Config:
        orm_mode = True