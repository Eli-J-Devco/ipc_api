import collections
import time

# Initialize consumption queue
consumption_queue = collections.deque(maxlen=10)

# Simulate adding values to the queue
for i in range(15):
    value = i * 10  # Simulate a value from the system
    print(f"Adding value: {value}")
    consumption_queue.append(value)
    print(f"Queue contents: {list(consumption_queue)}")
    print(f"Average consumption: {sum(consumption_queue) / len(consumption_queue)}")
    time.sleep(1)  # Simulate a 1-second delay
