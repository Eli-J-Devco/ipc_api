from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import config


class RegisterBlock(config.Base):
    __tablename__ = "register_block"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_template: Mapped[int] = mapped_column(Integer,
                                             ForeignKey("template_library.id",
                                                        ondelete="CASCADE",
                                                        onupdate="CASCADE"), nullable=False)
    addr: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    id_type_function: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id"), nullable=False)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)

    template_library = relationship("Template", foreign_keys=[id_template])
    type_function = relationship("ConfigInformation", foreign_keys=[id_type_function])

