import os
import pathlib

from src.subscriber import run_subscriber
from src.logger.logger import setup_logging

# LOG_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "logs")
# if os.path.exists(LOG_PATH) is False:
#     os.makedirs(LOG_PATH)

setup_logging(file_name="subscriber", log_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "logs"))
if __name__ == '__main__':
    run_subscriber()
