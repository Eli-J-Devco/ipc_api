import os
from datetime import datetime

import yaml
import logging.config
import logging
import coloredlogs
import pathlib


def setup_logging(default_path='config.yaml',
                  default_level=logging.INFO,
                  env_key='LOG_CFG',
                  file_name=None,
                  log_path=None):
    if not log_path:
        log_path = pathlib.Path(__file__).parent.absolute()
    if not file_name:
        file_name = ""
    now = datetime.now().strftime("%Y%m%d")
    file_name = f"{now}_{file_name}.log"

    path = pathlib.Path(__file__).parent.absolute()
    path = os.path.join(path, default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value

    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                for handler in config['handlers']:
                    if 'filename' in config['handlers'][handler]:
                        config['handlers'][handler]['filename'] = os.path.join(log_path,
                                                                               file_name)
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')

    return logging.getLogger()