
# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import base64
import collections
import datetime
import gzip
import json
import logging
import os
import platform
import sys
from datetime import datetime

import mqttools
import psutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *
from getCPU import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)
############################################################################ CPU ############################################################################
# Describe get_size cpu 
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def getReadableSize(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} YB"
# Describe convertBytesToReadable  
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def convertBytesToReadable(bytes_value, unit="KB"):
    if unit == "KB":
        return f"{bytes_value / 1024:.2f} KB"
    elif unit == "MB":
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    elif unit == "GB":
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_value} B"

# Function get system information
def getSystemInformation():
    uname = platform.uname()
    return {
        "System": uname.system,
        "NodeName": uname.node,
        "Release": uname.release,
        "Version": uname.version,
        "Machine": uname.machine,
        "Processor": uname.processor
    }
# Function to get startup time
def getBootTime():
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    return f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"

# Function to get CPU information
def getCpuInformation():
    return {
        "Physicalcores": psutil.cpu_count(logical=False),
        "Totalcores": psutil.cpu_count(logical=True),
        "MaxFrequency": f"{psutil.cpu_freq().max:.2f}Mhz",
        "MinFrequency": f"{psutil.cpu_freq().min:.2f}Mhz",
        "CurrentFrequency": f"{psutil.cpu_freq().current:.2f}Mhz",
        "TotalCPUUsage": f"{psutil.cpu_percent()}%"
    }

# # Function to get memory information
def getMemoryInformation():
    svmem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "Total": getReadableSize(svmem.total),
        "Available": getReadableSize(svmem.available),
        "Used": getReadableSize(svmem.total - svmem.available),
        "UsedReal": getReadableSize(svmem.used),
        "Free": getReadableSize(svmem.free),
        "Percentage": f"{svmem.percent:.1f}%",
        "SWAP": {
            "Total": getReadableSize(swap.total),
            "Free": getReadableSize(swap.free),
            "Used": getReadableSize(swap.used),
            "Percentage": f"{swap.percent}%"
        }
    }

# Function to get disk information
def getDiskInformation():
    total_disk_size = 0
    total_disk_used = 0
    disk_partitions = psutil.disk_partitions()
    unique_partitions = {}

    for partition in disk_partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            partition_key = f"{partition_usage.total}_{partition_usage.used}_{partition_usage.free}"

            if partition_key in unique_partitions:
                continue

            unique_partitions[partition_key] = {
                "MountPoint": partition.mountpoint,
                "TotalSize": getReadableSize(partition_usage.total),
                "Used": getReadableSize(partition_usage.used),
                "Free": getReadableSize(partition_usage.free),
                "Percentage": f"{(partition_usage.used / partition_usage.total) * 100:.1f}%"
            }

            total_disk_size += partition_usage.total
            total_disk_used += partition_usage.used
        except PermissionError:
            continue

    return {
        "TotalSize": getReadableSize(total_disk_size),
        "Used": getReadableSize(total_disk_used),
        "Free": getReadableSize(total_disk_size - total_disk_used),
        "Percentage": f"{(total_disk_used / total_disk_size) * 100:.1f}%"
    }

# Function to get network information
def getNetworkInformation():
    network_info = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                network_info[interface_name] = {
                    "IPAddress": address.address,
                    "Netmask": address.netmask,
                    "BroadcastIP": address.broadcast
                }
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                network_info[interface_name] = {
                    "MACAddress": address.address,
                    "Netmask": address.netmask,
                    "BroadcastMAC": address.broadcast
                }
    return network_info

# Function to get network speed information
def getNetworkSpeedInformation(net_io_counters_prev):
    net_io_counters = psutil.net_io_counters()
    current_time = datetime.datetime.now()
    time_diff = (current_time - net_io_counters_prev["Timestamp"]).total_seconds()

    upstream = convertBytesToReadable((net_io_counters.bytes_sent - net_io_counters_prev["TotalSent"]) / time_diff, unit="KB")
    downstream = convertBytesToReadable((net_io_counters.bytes_recv - net_io_counters_prev["TotalReceived"]) / time_diff, unit="KB")
    print("time_diff 1",time_diff)
    net_io_counters_prev["TotalSent"] = net_io_counters.bytes_sent
    net_io_counters_prev["TotalReceived"] = net_io_counters.bytes_recv
    net_io_counters_prev["Timestamp"] = current_time

    return {
        "Upstream": upstream,
        "Downstream": downstream,
        "TotalSent": getReadableSize(net_io_counters.bytes_sent),
        "TotalReceived": getReadableSize(net_io_counters.bytes_recv),
        "Timestamp": f"{current_time.hour}:{current_time.minute}:{current_time.second}"
    }

# Function to get disk I/O information
def getDiskIoInformation(disk_io_counters_prev):
    disk_io_counters = psutil.disk_io_counters()
    current_time = datetime.datetime.now()
    time_diff = (current_time - disk_io_counters_prev["Timestamp"]).total_seconds()
    print("time_diff 2",time_diff)
    disk_io_counters_prev["ReadBytes"] = disk_io_counters.read_bytes
    disk_io_counters_prev["WriteBytes"] = disk_io_counters.write_bytes
    disk_io_counters_prev["Timestamp"] = current_time

    return {
        "SpeedRead": convertBytesToReadable((disk_io_counters.read_bytes - disk_io_counters_prev["ReadBytes"]) / time_diff, unit="KB"),
        "SpeedWrite": convertBytesToReadable((disk_io_counters.write_bytes - disk_io_counters_prev["WriteBytes"]) / time_diff, unit="KB"),
        "ReadBytes": getReadableSize(disk_io_counters.read_bytes),
        "WriteBytes": getReadableSize(disk_io_counters.write_bytes),
        "Timestamp": f"{current_time.hour}:{current_time.minute}:{current_time.second}"
    }
