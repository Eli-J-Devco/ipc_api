import psutil
import datetime

# Hàm chuyển đổi bytes thành đơn vị dễ đọc
def convertBytesToReadable(size, unit="B"):
    units = ["B", "KB", "MB", "GB", "TB"]
    index = units.index(unit)
    return size / (1024 ** index)

# Hàm chuyển đổi số lượng bytes thành đơn vị đọc dễ dàng
def getReadableSize(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

# Lấy thông tin đếm IO đĩa trước đó
disk_io_counters_prev = {
    "ReadCount": 0,
    "WriteCount": 0,
    "ReadBytes": 0,
    "WriteBytes": 0,
    "Timestamp": datetime.datetime.now()
}

# Lấy thông tin IO hiện tại và tính toán tốc độ đọc/ghi
def get_disk_io_info():
    disk_io_counters = psutil.disk_io_counters()
    current_time = datetime.datetime.now()
    time_diff = (current_time - disk_io_counters_prev["Timestamp"]).total_seconds()
    
    # Tính toán tốc độ đọc và ghi
    SpeedRead = convertBytesToReadable((disk_io_counters.read_bytes - disk_io_counters_prev["ReadBytes"]) / time_diff, unit="KB")
    SpeedWrite = convertBytesToReadable((disk_io_counters.write_bytes - disk_io_counters_prev["WriteBytes"]) / time_diff, unit="KB")
    
    # Cập nhật thông tin đọc/ghi hiện tại
    disk_io_counters_prev["ReadBytes"] = disk_io_counters.read_bytes
    disk_io_counters_prev["WriteBytes"] = disk_io_counters.write_bytes
    disk_io_counters_prev["Timestamp"] = current_time
    
    # Trả về thông tin IO
    return {
        "SpeedRead": SpeedRead,
        "SpeedWrite": SpeedWrite,
        "ReadBytes": getReadableSize(disk_io_counters.read_bytes),
        "WriteBytes": getReadableSize(disk_io_counters.write_bytes),
        "Timestamp": f"{current_time.hour}:{current_time.minute}:{current_time.second}"
    }

# Lấy thông tin Disk IO
system_info = {"DiskIO": get_disk_io_info()}
print(system_info)
