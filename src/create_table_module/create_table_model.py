import typing

from sqlalchemy import TIMESTAMP, INTEGER, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.type_api import TypeEngine


class ColumnConfig:
    def __init__(self,
                 name: str,
                 col_type: TypeEngine,
                 nullable: bool,
                 primary_key: bool,
                 foreign_key: typing.Optional[dict] = None,):
        self.name = name
        self.col_type = col_type
        self.nullable = nullable
        self.primary_key = primary_key
        self.foreign_key = foreign_key

    def dict(self):
        return {
            "name": self.name,
            "type": self.col_type,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "foreign_key": self.foreign_key
        }


class CreateTableModel:
    default = {
        "time": ColumnConfig(name="time", col_type=TIMESTAMP, nullable=False, primary_key=True),
        "id_device": ColumnConfig(name="id_device", col_type=INTEGER, nullable=False, primary_key=False,
                                  foreign_key={
                                        "name": "device_list.id",
                                        "ondelete": "CASCADE",
                                        "onupdate": "CASCADE"
                                  }),
        "error": ColumnConfig(name="error", col_type=INTEGER, nullable=True, primary_key=False),
        "low_alarm": ColumnConfig(name="low_alarm", col_type=INTEGER, nullable=True, primary_key=False),
        "high_alarm": ColumnConfig(name="high_alarm", col_type=INTEGER, nullable=True, primary_key=False),
        "serial_number": ColumnConfig(name="serial_number", col_type=String(255), nullable=True, primary_key=False),
    }
