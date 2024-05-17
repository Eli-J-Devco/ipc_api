import numpy as np
import matplotlib.pyplot as plt
import time
import threading
from queue import Queue  # Import thư viện Queue

def kalman_filter(measurement, Q, R, x_hat, P):
    K = P / (P + R)
    x_hat = x_hat + K * (measurement - x_hat)
    P = (1 - K) * P + Q
    return x_hat, P

class KalmanFilterThread(threading.Thread):
    def __init__(self, measurement_queue, filtered_value_queue):
        super().__init__()
        self.measurement_queue = measurement_queue
        self.filtered_value_queue = filtered_value_queue
        self.Q = 0.009 # Giảm process noise covariance
        self.R = 0.01   # Giảm measurement noise covariance
        self.x_hat = 0  # Initial state estimate
        self.P = 1  # Initial error covariance
        self.total_input = 0
        self.total_filtered = 0

    def run(self):
        while True:
            # Lấy dữ liệu đầu vào từ hàng đợi
            measurement = self.measurement_queue.get()
            if measurement is None:
                break

            # Lọc dữ liệu và cập nhật trạng thái
            x_hat, P = kalman_filter(measurement, self.Q, self.R, self.x_hat, self.P)

            # Cập nhật tổng giá trị đầu vào và lọc
            self.total_input += measurement
            self.total_filtered += x_hat

            # Thêm giá trị lọc vào hàng đợi
            self.filtered_value_queue.put(x_hat)

        # In ra tổng giá trị đầu vào và lọc
        print(f"Tổng giá trị đầu vào: {self.total_input}")
        print(f"Tổng giá trị đã được lọc: {self.total_filtered}")
        print(f"Sự chênh lệch giữa tổng giá trị: {abs(self.total_input - self.total_filtered)}")

def test_kalman_filter():
    # Tạo hàng đợi cho dữ liệu đầu vào và lọc
    measurement_queue = Queue()  # Khai báo Queue cho dữ liệu đầu vào
    filtered_value_queue = Queue()  # Khai báo Queue cho giá trị lọc

    # Khởi tạo và khởi chạy luồng bộ lọc Kalman
    kalman_filter_thread = KalmanFilterThread(measurement_queue, filtered_value_queue)
    kalman_filter_thread.start()

    # Mô phỏng dữ liệu thời gian thực
    for i in range(100):
        # Tạo dữ liệu đầu vào ngẫu nhiên
        measurement = np.random.randint(0, 100)

        # Thêm dữ liệu đầu vào vào hàng đợi
        measurement_queue.put(measurement)

        # Lấy giá trị lọc từ hàng đợi
        filtered_value = filtered_value_queue.get()
        if filtered_value is None:
            break

        print(f"Measurement: {measurement}, Filtered Value: {filtered_value}")

    # Dừng luồng bộ lọc Kalman
    measurement_queue.put(None)
    kalman_filter_thread.join()

if __name__ == "__main__":
    test_kalman_filter()
