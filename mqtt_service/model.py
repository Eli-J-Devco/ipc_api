import typing

from pydantic import BaseModel


class MetaData(BaseModel):
    retry: int = 3


class Topic(BaseModel):
    target: str
    failed: str


class MessageModel(BaseModel):
    metadata: MetaData
    topic: Topic
    message: typing.Optional[typing.Dict[str, typing.Any]] = None
    error: typing.Optional[str] = None
