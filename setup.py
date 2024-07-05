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
    abs_dirname = PATH
    pid = f'API_V2'
    if sys.platform == 'win32':
        # use run with window
        subprocess.Popen(
            f'pm2 start {abs_dirname}/api/main.py -f --name "{pid}" --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(f'sudo pm2 delete {pid}', shell=True).communicate()
        subprocess.Popen(
            f'sudo pm2 start {abs_dirname}/main.py --interpreter {abs_dirname}/venv/bin/python3 -f --name "{pid}" '
            f'--restart-delay=10000', shell=True).communicate()


init_api_web()
