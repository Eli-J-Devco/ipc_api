from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Định nghĩa mô hình SQLAlchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProjectSetupDB(Base):
    __tablename__ = 'project_setup'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    serial_number = Column(String(255))
    location = Column(String(255))
    description = Column(String(255))
    administrative_contact = Column(String(255))
    id_first_page_on_login = Column(Integer)
    id_logging_interval = Column(Integer)
    id_scheduled_upload_time = Column(Integer)
    number_times_retry = Column(Integer)
    id_time_wait_before_retry = Column(Integer)
    id_upload_debug_information = Column(Integer)
    enable_upload_data_on_alarm_status = Column(Integer)
    enable_upload_data_on_low_disk = Column(Integer)
    enable_upload_data_on_system_startup = Column(Integer)
    link_remote_access = Column(String(255))
    allow_remote_access = Column(Integer)
    id_time_zone = Column(Integer)
    Time1cycle = Column(Float)
    sampling_time1cycle = Column(Float)
    mode = Column(Integer)
    control_mode = Column(Integer)
    value_offset_zero_export = Column(Float)
    value_power_limit = Column(Float)
    value_offset_power_limit = Column(Float)
    powermeter_target_point = Column(Float)
    powermeter_tolerance = Column(Float)
    powermeter_max_point = Column(Float)
    slow_approx_limit_in_percent = Column(Integer)
    slow_approx_factor_in_percent = Column(Integer)
    loop_interval_in_seconds = Column(Integer)
    set_limit_delay_in_seconds = Column(Integer)
    set_limit_timeout_seconds = Column(Integer)
    set_limit_delay_in_seconds_multiple_inverter = Column(Integer)
    poll_interval_in_seconds = Column(Integer)
    on_grid_usage_jump_to_limit_percent = Column(Integer)
    max_difference_between_limit_and_outputpower = Column(Integer)
    set_limit_retry = Column(Integer)
    set_power_status_delay_in_seconds = Column(Integer)
    modhopper1 = Column(Integer)
    modhopper2 = Column(Integer)
    modhopper_key = Column(String(255))
    modhopper_rf_config = Column(Integer)
    modhopper_rf_channel = Column(Integer)
    status = Column(Integer)

# Định nghĩa mô hình Pydantic
class ProjectSetup(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None
    id_first_page_on_login: Optional[int] = None
    id_logging_interval: Optional[int] = None
    id_scheduled_upload_time: Optional[int] = None
    number_times_retry: Optional[int] = None
    id_time_wait_before_retry: Optional[int] = None
    id_upload_debug_information: Optional[int] = None
    enable_upload_data_on_alarm_status: Optional[bool] = None
    enable_upload_data_on_low_disk: Optional[bool] = None
    enable_upload_data_on_system_startup: Optional[bool] = None
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None
    id_time_zone: Optional[int] = None
    Time1cycle: Optional[float] = None
    sampling_time1cycle: Optional[float] = None
    mode: Optional[int] = None
    control_mode: Optional[int] = None
    value_offset_zero_export: Optional[float] = None
    value_power_limit: Optional[float] = None
    value_offset_power_limit: Optional[float] = None
    powermeter_target_point: Optional[float] = None
    powermeter_tolerance: Optional[float] = None
    powermeter_max_point: Optional[float] = None
    slow_approx_limit_in_percent: Optional[int] = None
    slow_approx_factor_in_percent: Optional[int] = None
    loop_interval_in_seconds: Optional[int] = None
    set_limit_delay_in_seconds: Optional[int] = None
    set_limit_timeout_seconds: Optional[int] = None
    set_limit_delay_in_seconds_multiple_inverter: Optional[int] = None
    poll_interval_in_seconds: Optional[int] = None
    on_grid_usage_jump_to_limit_percent: Optional[int] = None
    max_difference_between_limit_and_outputpower: Optional[int] = None
    set_limit_retry: Optional[int] = None
    set_power_status_delay_in_seconds: Optional[int] = None
    modhopper1: Optional[int] = None
    modhopper2: Optional[int] = None
    modhopper_key: Optional[str] = None
    modhopper_rf_config: Optional[int] = None
    modhopper_rf_channel: Optional[int] = None
    status: Optional[bool] = None

# Tạo kết nối đến cơ sở dữ liệu
DATABASE_URL = "mysql+pymysql://nextwave_dev:jB8FC6tEkHLjPaGB@103.7.43.228:3006/nextwave_ipc_dev"
from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)
Session = sessionmaker(bind=engine)

# Hàm truy vấn tất cả dữ liệu từ bảng project_setup
def get_all_project_setup():
    with Session() as session:
        results = session.query(ProjectSetupDB).all()
        return [ProjectSetup.from_orm(project) for project in results]

# Ví dụ sử dụng hàm
if __name__ == "__main__":
    project_setups = get_all_project_setup()
    for project in project_setups:
        print(project.json())
