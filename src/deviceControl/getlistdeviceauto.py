import platform
import psutil
import datetime
import time

def extract_device_info(item):
    if 'id_device' in item and 'mode' in item and 'status_device' in item:
        id_device = item['id_device']
        mode = item['mode']
        status_device = item['status_device']
        p_max = item['rated_power']
        p_max_custom = item.get('rated_power_custom', p_max)
        p_min_percent = item['min_watt_in_percent']
        p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
        value = get_device_value(item, "ControlINV")
        if value is None:
            return None
        operator = get_device_value(item, "OperatingState")
        if operator is None:
            return None
        slope = get_device_value(item, "WMax", field_key='slope')
        if slope is None:
            return None
        results_device_type = item.get('name_device_type')  # Lấy giá trị loại thiết bị
        if results_device_type is None:
            return None
        return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
    return None

def get_device_value(item, point_key, field_key='value'):
    array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
            for field in param.get("fields", []) if field["point_key"] == point_key]
    return array[0] if array else None

def is_device_controlable(results_device_type, status_device, mode, operator):
    return (results_device_type == "PV System Inverter" and 
            status_device == 'online' and 
            mode == 1 and 
            operator not in [7, 8])
