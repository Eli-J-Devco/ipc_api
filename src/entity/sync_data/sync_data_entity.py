import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from configs.config import DBSessionManager

class SyncData(DBSessionManager.Base):
    __tablename__ = 'sync_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_device: Mapped[int] = mapped_column(Integer, nullable=False)
    synced: Mapped[int] = mapped_column(Integer, nullable=True)
    data: Mapped[str] = mapped_column(String(500))
    id_upload_channel: Mapped[int] = mapped_column(Integer)
    modbusport: Mapped[int] = mapped_column(Integer)
    modbusdevice: Mapped[int] = mapped_column(Integer)
    ensuredir: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255))
    deletedfile: Mapped[int] = mapped_column(Integer, nullable=True)
    createtime: Mapped[datetime.datetime] = mapped_column(DateTime)
    updatetime: Mapped[datetime.datetime] = mapped_column(DateTime)
    error: Mapped[str] = mapped_column(String(255))
    number_of_time_retry: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=True, default=1)