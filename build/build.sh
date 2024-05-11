#!/bin/bash
if [ -d /home/jenkins/ ]; then echo 'Exists'; else mkdir "/home/jenkins/"; fi
if [ -d /home/jenkins/sources/ ]; then echo 'Exists'; else mkdir "/home/jenkins/sources/"; fi
cp -rf /var/lib/jenkins/workspace/api_python_new/ /home/jenkins/sources/api_python_new/
cd /home/jenkins/sources/api_python_new/ || exit
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt  --no-cache-dir
cp ./ipc_api/.env.example ./ipc_api/.env