from pydantic.main import BaseModel


class GetRegisterBlockFilter(BaseModel):
    id_template: int
