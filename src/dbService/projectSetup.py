# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from dbEntity.project_setup.project_setup_entity import *
from dbModel.project_setup_model import ProjectSetupModel 
import logging
logger = logging.getLogger(__name__)
class ProjectSetupService:
    @staticmethod
    async def selectAllProjectSetup(session: AsyncSession):
        try:
            query = select(ProjectSetup)
            result = await session.execute(query)
            projects = result.scalars().all()

            return [
                ProjectSetupModel(**{
                    "id": project.id,
                    "name": project.name,
                    "serial_number": project.serial_number,
                    "location": project.location,
                    "description": project.description,
                    "administrative_contact": project.administrative_contact,
                    "enable_upload_data_on_alarm_status": project.enable_upload_data_on_alarm_status,
                    "enable_upload_data_on_low_disk": project.enable_upload_data_on_low_disk,
                    "enable_upload_data_on_system_startup": project.enable_upload_data_on_system_startup,
                    "link_remote_access": project.link_remote_access,
                    "allow_remote_access": project.allow_remote_access,
                    "enable_static_routing": project.enable_static_routing,
                    "mode": project.mode,
                    "Time1cycle": project.Time1cycle,
                    "sampling_time1cycle": project.sampling_time1cycle,
                    "control_mode": project.control_mode,
                    "value_offset_zero_export": project.value_offset_zero_export,
                    "threshold_zero_export": project.threshold_zero_export,
                    "value_power_limit": project.value_power_limit,
                    "value_offset_power_limit": project.value_offset_power_limit,
                    "kp_zero_export": project.kp_zero_export,
                    "ki_zero_export": project.ki_zero_export,
                    "kd_zero_export": project.kd_zero_export,
                    "delta_time_zero_export": project.delta_time_zero_export,
                    "kp_power_limit": project.kp_power_limit,
                    "ki_power_limit": project.ki_power_limit,
                    "kd_power_limit": project.kd_power_limit,
                    "delta_time_power_limit": project.delta_time_power_limit,
                    "value_zero_export": project.value_zero_export,
                    "enable_power_limit": project.enable_power_limit,
                    "powermeter_target_point": project.powermeter_target_point,
                    "enable_zero_export": project.enable_zero_export,
                    "powermeter_tolerance": project.powermeter_tolerance,
                    "powermeter_max_point": project.powermeter_max_point,
                    "slow_approx_limit_in_percent": project.slow_approx_limit_in_percent,
                    "slow_approx_factor_in_percent": project.slow_approx_factor_in_percent,
                    "loop_interval_in_seconds": project.loop_interval_in_seconds,
                    "set_limit_delay_in_seconds": project.set_limit_delay_in_seconds,
                    "set_limit_timeout_seconds": project.set_limit_timeout_seconds,
                    "set_limit_delay_in_seconds_multiple_inverter": project.set_limit_delay_in_seconds_multiple_inverter,
                    "poll_interval_in_seconds": project.poll_interval_in_seconds,
                    "on_grid_usage_jump_to_limit_percent": project.on_grid_usage_jump_to_limit_percent,
                    "max_difference_between_limit_and_outputpower": project.max_difference_between_limit_and_outputpower,
                    "set_limit_retry": project.set_limit_retry,
                    "set_power_status_delay_in_seconds": project.set_power_status_delay_in_seconds,
                    "enable_search_modbus_rtu_device": project.enable_search_modbus_rtu_device,
                    "modhopper1": project.modhopper1,
                    "modhopper2": project.modhopper2,
                    "modhopper_key": project.modhopper_key,
                    "modhopper_rf_config": project.modhopper_rf_config,
                    "modhopper_rf_channel": project.modhopper_rf_channel,
                    "mqtt_broker_cloud": project.mqtt_broker_cloud,
                    "mqtt_port_cloud": project.mqtt_port_cloud,
                    "mqtt_username_cloud": project.mqtt_username_cloud,
                    "mqtt_password_cloud": project.mqtt_password_cloud,
                    "low_performance": project.low_performance,
                    "high_performance": project.high_performance,
                    "status": project.status,
                })
                for project in projects
            ] 
        except Exception as e:
            logger.error("Error in selectAllProjectSetup: ", e)
            return []
        finally:
            await session.close()
    @staticmethod
    async def updateProjectSetup(session: AsyncSession, updates: dict):
        try:
            query = select(ProjectSetup)
            result = await session.execute(query)
            project = result.scalars().one_or_none()

            if project is None:
                logger.info("No project found to update.")
                return None

            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
                else:
                    logger.info(f"Attribute {key} does not exist on ProjectSetup.")

            await session.commit()
            return project.__dict__ 
        except Exception as e:
            logger.error("Error in updateProjectSetup: ", e)
            await session.rollback() 
            return None
        finally:
            await session.close()
    @staticmethod
    async def selectTimeLogInterval(session: AsyncSession):
        try:
            query = (
                select(ConfigInformation.name.label("time_log_interval"))
                .join(ProjectSetup, ProjectSetup.id_logging_interval == ConfigInformation.id)
            )
            result = await session.execute(query)
            time_log_intervals = result.scalars().all()
            extracted_values = [int(interval.split()[0]) for interval in time_log_intervals if interval]
            return extracted_values 
        except Exception as e:
            logger.error("Error in selectTimeLogInterval: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def select_time_sync_cloud(session: AsyncSession):
        try:
            query = (
                select(ConfigInformation.value.label("time_sync_server"))
                .join(ProjectSetup, ProjectSetup.id_scheduled_upload_time == ConfigInformation.id)
            )
            result = await session.execute(query)
            time_log_data_servers = result.scalars().all()
            return time_log_data_servers[0]
        except Exception as e:
            logger.error("Error in selectScheduledUploadTime: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def get_time_retry(session: AsyncSession):
        try:
            query = (
                select(ConfigInformation.value
                .label("time_retry"))
                .join(ProjectSetup, ProjectSetup.id_time_wait_before_retry == ConfigInformation.id)
            )
            result = await session.execute(query)
            time_retry = result.scalar()
            return time_retry
        except Exception as e:
            logger.error("Error in get_time_log_data_server: ", e)
            return None
        finally:
            await session.close()
    