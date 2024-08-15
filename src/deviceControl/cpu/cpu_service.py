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

class CPUInfo:
    def __init__(self):
        pass

    @staticmethod
    def get_readable_size(size_bytes):
        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} YB"

    @staticmethod
    def convert_bytes_to_readable(bytes_value, unit="KB"):
        if unit == "KB":
            return f"{bytes_value / 1024:.2f} KB"
        elif unit == "MB":
            return f"{bytes_value / (1024 ** 2):.2f} MB"
        elif unit == "GB":
            return f"{bytes_value / (1024 ** 3):.2f} GB"
        else:
            return f"{bytes_value} B"

    @staticmethod
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

    @staticmethod
    def getBootTime():
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        return f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"

    @staticmethod
    def getCpuInformation():
        return {
            "PhysicalCores": psutil.cpu_count(logical=False),
            "TotalCores": psutil.cpu_count(logical=True),
            "MaxFrequency": f"{psutil.cpu_freq().max:.2f} MHz",
            "MinFrequency": f"{psutil.cpu_freq().min:.2f} MHz",
            "CurrentFrequency": f"{psutil.cpu_freq().current:.2f} MHz",
            "TotalCPUUsage": f"{psutil.cpu_percent()}%"
        }

    @staticmethod
    def getMemoryInformation():
        svmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "Total": CPUInfo.get_readable_size(svmem.total),
            "Available": CPUInfo.get_readable_size(svmem.available),
            "Used": CPUInfo.get_readable_size(svmem.total - svmem.available),
            "UsedReal": CPUInfo.get_readable_size(svmem.used),
            "Free": CPUInfo.get_readable_size(svmem.free),
            "Percentage": f"{svmem.percent:.1f}%",
            "SWAP": {
                "Total": CPUInfo.get_readable_size(swap.total),
                "Free": CPUInfo.get_readable_size(swap.free),
                "Used": CPUInfo.get_readable_size(swap.used),
                "Percentage": f"{swap.percent}%"
            }
        }

    @staticmethod
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
                    "TotalSize": CPUInfo.get_readable_size(partition_usage.total),
                    "Used": CPUInfo.get_readable_size(partition_usage.used),
                    "Free": CPUInfo.get_readable_size(partition_usage.free),
                    "Percentage": f"{(partition_usage.used / partition_usage.total) * 100:.1f}%"
                }

                total_disk_size += partition_usage.total
                total_disk_used += partition_usage.used
            except PermissionError:
                continue

        return {
            "TotalSize": CPUInfo.get_readable_size(total_disk_size),
            "Used": CPUInfo.get_readable_size(total_disk_used),
            "Free": CPUInfo.get_readable_size(total_disk_size - total_disk_used),
            "Percentage": f"{(total_disk_used / total_disk_size) * 100:.1f}%"
        }

    @staticmethod
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

    @staticmethod
    def getNetworkSpeedInformation(net_io_counters_prev):
        net_io_counters = psutil.net_io_counters()
        current_time = datetime.now()
        time_diff = (current_time - net_io_counters_prev["Timestamp"]).total_seconds()
        if time_diff < 1:
            return None  
        else:
            upstream = CPUInfo.convert_bytes_to_readable((net_io_counters.bytes_sent - net_io_counters_prev["TotalSent"]) / time_diff, unit="KB")
            downstream = CPUInfo.convert_bytes_to_readable((net_io_counters.bytes_recv - net_io_counters_prev["TotalReceived"]) / time_diff, unit="KB")
            net_io_counters_prev["TotalSent"] = net_io_counters.bytes_sent
            net_io_counters_prev["TotalReceived"] = net_io_counters.bytes_recv
            net_io_counters_prev["Timestamp"] = current_time
        return {
            "Upstream": upstream,
            "Downstream": downstream,
            "TotalSent": CPUInfo.get_readable_size(net_io_counters.bytes_sent),
            "TotalReceived": CPUInfo.get_readable_size(net_io_counters.bytes_recv),
            "Timestamp": f"{current_time.hour}:{current_time.minute}:{current_time.second}"
        }

    @staticmethod
    def getDiskIoInformation(disk_io_counters_prev):
        disk_io_counters = psutil.disk_io_counters()
        current_time = datetime.now()
        time_diff = (current_time - disk_io_counters_prev["Timestamp"]).total_seconds()
        if time_diff < 2:
            return None
        else:
            speed_read = CPUInfo.convert_bytes_to_readable((disk_io_counters.read_bytes - disk_io_counters_prev["ReadBytes"]) / time_diff, unit="KB")
            speed_write = CPUInfo.convert_bytes_to_readable((disk_io_counters.write_bytes - disk_io_counters_prev["WriteBytes"]) / time_diff, unit="KB")
            disk_io_counters_prev["ReadBytes"] = disk_io_counters.read_bytes
            disk_io_counters_prev["WriteBytes"] = disk_io_counters.write_bytes
            disk_io_counters_prev["Timestamp"] = current_time
            return {
                "SpeedRead": speed_read,
                "SpeedWrite": speed_write,
                "ReadBytes": CPUInfo.get_readable_size(disk_io_counters.read_bytes),
                "WriteBytes": CPUInfo.get_readable_size(disk_io_counters.write_bytes),
                "Timestamp": f"{current_time.hour}:{current_time.minute}:{current_time.second}"
            }