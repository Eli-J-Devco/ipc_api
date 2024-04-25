from pydantic.main import BaseModel


class GetTemplateFilter(BaseModel):
    type: int = 1
