import subprocess
import sys
from pathlib import Path

PATH = Path(__file__).parent.absolute()

pids = ["DEVICE_SERVICE", "SINGLE_LINE_DIAGRAM_SERVICE"]


def init(path: str, pid: str):
    abs_dirname = PATH
    subprocess.Popen(
        f'sudo pm2 start {abs_dirname}/{path}/main.py --interpreter {abs_dirname}/.venv/bin/python3 -f --name "{pid}" '
        f'--restart-delay=10000', shell=True).communicate()


def clear(pid: str):
    # use run with ubuntu/linux
    subprocess.Popen(
        f'sudo pm2 delete {pid}', shell=True).communicate()


if __name__ == '__main__':
    if sys.platform == 'win32':
        print("Windows is not supported")
        sys.exit()

    for pid in pids:
        print(f"Starting {pid}")
        clear(pid)
        init(pid.lower(), pid)

