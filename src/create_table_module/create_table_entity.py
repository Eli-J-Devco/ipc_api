from sqlalchemy import INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from .config import orm_provider as config


class Devices(config.Base):
    __tablename__ = "device_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
