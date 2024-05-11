#!/bin/bash
su -c ipc
echo "$USER"
rm -rf /home/ipc/sources/api_python_new/
cp -rf /var/lib/jenkins/workspace/api_python_new/ /home/ipc/sources/api_python_new/
cd /home/ipc/sources/api_python_new/ || exit
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt  --no-cache-dir