from sqlalchemy import Column, TIMESTAMP, INTEGER, ForeignKey, String


class CreateTableModel:
    default = [Column("time", TIMESTAMP, primary_key=True, nullable=False),
               Column("id_device", INTEGER, ForeignKey("device_list.id")),
               Column("error", INTEGER, nullable=True),
               Column("low_alarm", INTEGER, nullable=True),
               Column("high_alarm", INTEGER, nullable=True),
               Column("serial_number", String(255), nullable=True)]
