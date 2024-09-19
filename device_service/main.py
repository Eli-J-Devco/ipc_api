from src.subscriber import run_subscriber
from src.logger.logger import setup_logging

setup_logging()

if __name__ == '__main__':
    run_subscriber()
