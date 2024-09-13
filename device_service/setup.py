import subprocess
import sys
from pathlib import Path

PATH = Path(__file__).parent.absolute()

pid = f'INIT_DEVICE_SERVICE'


def init():
    abs_dirname = PATH
    if sys.platform == 'win32':
        # use run with window
        subprocess.Popen(
            f'pm2 start {abs_dirname}/api/main.py -f --name "{pid}" --restart-delay=10000', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 start {abs_dirname}/main.py --interpreter {abs_dirname}/venv/bin/python3 -f --name "{pid}" '
            f'--restart-delay=10000', shell=True).communicate()


def clear():
    if sys.platform == 'win32':
        # use run with window
        subprocess.Popen(
            f'pm2 delete {pid}', shell=True).communicate()
    else:
        # use run with ubuntu/linux
        subprocess.Popen(
            f'sudo pm2 delete {pid}', shell=True).communicate()


clear()
init()
