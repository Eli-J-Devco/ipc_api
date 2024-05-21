# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import subprocess
import sys
from pathlib import Path

PATH = Path(__file__).parent.absolute()


def init_api_web():
    absDirname = PATH
    pid = f'API_V2'
    if sys.platform == 'win32':
        # use run with window
        subprocess.Popen(
            f'pm2 start {absDirname}/api/main.py -f --name "{pid}" --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {absDirname}/main.py --interpreter {absDirname}/venv/bin/python3 -f --name "{pid}" '
            f'--restart-delay=10000', shell=True).communicate()


init_api_web()
