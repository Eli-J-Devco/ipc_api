# scada
<!--  -->
https://ubuntu.com/download/alternative-downloads
<!-- How do I disable the screensaver/lock in kali linux? -->
Settings > Power Manager > Security
unchecked Lockscreen when system is going to sleep
<!-- Disable auto logout -->
Setting > Privacy > Screen Lock > Automatic Screen Lock (Off)
<!-- Language Python -->
sudo apt-get update
sudo apt-get install python
pip --version

<!-- pip -->
sudo apt-get install pip
or sudo apt install python3-pip
<!-- Project -->
python -m venv venv
source venv/Scripts/activate
pip3 install -r requirements.txt  --no-cache-dir
<!-- linux -->
python3 -m venv venv
source venv/bin/activate
deactivate

<!--  -->
D:\..\project\ipc_api\venv\Scripts\python D:\..\project\ipc_api\main.py
sudo /home/ipc/python/project1/venv/bin/python3.10 /home/ipc/python/project1/main.py
sudo /sources/python/api_python_new/venv/bin/python3.10 /sources/python/api_python_new/main.py
<!-- install all package python -->
pip install -r requirements.txt
pip3 install -r requirements.txt  --no-cache-dir

pydantic-settings==2.1.0
pydantic==2.5.3
pydantic-settings==2.1.0
pydantic_core==2.14.1
pydantic[email]
<!-- FastAPI -->
https://fastapi.tiangolo.com/
https://www.gormanalysis.com/blog/building-a-simple-crud-application-with-fastapi/
<!-- Run a Server Manually - Uvicorn -->
uvicorn main:app --host 0.0.0.0 --port 8000
<!-- Run a Server Manually - Uvicorn and auto reload -->
cd api_of_device
python main.py
python api_of_device/main.py
uvicorn main:app --reload 
http://127.0.0.1:8000/docs#/
<!-- Fast API JWT  -->
https://www.freecodecamp.org/news/how-to-add-jwt-authentication-in-fastapi/
import secrets
SECRET_KEY=secrets.token_hex()
<!-- Nodejs -->
sudo apt install nodejs npm
sudo apt install curl
curl -sSL https://deb.nodesource.com/setup_14.x | sudo bash -
sudo apt-get install -y nodejs
npm --version
node --version
<!-- Process Management -->
https://pm2.keymetrics.io/docs/usage/quick-start/
method1: sudo npm install pm2@latest
method2: sudo npm install pm2 -g
pm2 start /home/ipc/ipc_api/main.py --interpreter python3 -f  --name IPC|Main  --restart-delay=10000

<!-- Notes to self: installing PM2 on Windows, as a service -->
https://thomasswilliams.github.io/development/2020/04/07/installing-pm2-windows.html
<!-- Database -->
https://blog.hostvn.net/chia-se/huong-dan-cai-dat-mysql-tren-ubuntu-20.html
sudo apt install default-mysql-server
sudo mysql
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';

DROP USER 'ipc'@'%';
DROP USER 'root'@'localhost';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Nw$123654789';
CREATE USER 'ipc'@'%' IDENTIFIED WITH mysql_native_password BY 'Nw$123654789';
CREATE USER 'ipc'@'%' IDENTIFIED WITH standard BY 'Nw$123654789';
CREATE USER 'root'@'%' IDENTIFIED  BY 'Nw$123654789';
GRANT ALL PRIVILEGES ON * . * TO 'ipc'@'%';
GRANT ALL PRIVILEGES ON * . * TO 'root'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'ipc'@'%' WITH GRANT OPTION;
SELECT User, Host, Password FROM mysql.user;
<!-- connect to Remote MySQL Server (10061) -->
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql
<!-- Your password does not satisfy the current policy requirements -->
SHOW VARIABLES LIKE 'validate_password%';
SET GLOBAL validate_password.length = 4;
SET GLOBAL validate_password.policy=LOW;
SET GLOBAL validate_password.policy=LOW;
<!-- Commit MySQL -->
SELECT @@autocommit;
SET autocommit=0;
COMMIT;
<!-- MQTT -->
https://www.vultr.com/docs/install-mosquitto-mqtt-broker-on-ubuntu-20-04-server/
https://www.instructables.com/How-to-Use-MQTT-With-the-Raspberry-Pi-and-ESP8266/
sudo apt update 
sudo apt install -y mosquitto
<!-- set user and pass MQTT -->

sudo mosquitto_passwd -c /etc/mosquitto/pwfile nextwave
mosquitto_pub -d -u nextwave -P 123654789 -t IPC -m "Hello, World!"
mosquitto_sub -d -u nextwave -P 123654789  -t IPC
<!-- Deleting Mosquitto MQTT retained messages -->
sudo service mosquitto stop
sudo rm /var/lib/mosquitto/mosquitto.db
sudo service mosquitto start
<!-- Secure the Mosquitto Server -->
<!-- Tester client publish/Subscribe -->
https://mqtt-explorer.com/
sudo nano /etc/mosquitto/mosquitto.conf
sudo nano /etc/mosquitto/conf.d/default.conf

pid_file /run/mosquitto/mosquitto.pid
#bind_address 0.0.0.0
persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d
allow_anonymous false
password_file /etc/mosquitto/pwfile
listener 1883 0.0.0.0

<!-- Mosquito Server Refuses Connections Ubuntu 18.04 -->
sudo apt install ufw
sudo ufw status
<!-- Open Port 1883 and start firewall -->
sudo ufw allow 1883 
sudo ufw deny 1883
sudo ufw enable
<!-- Verify Mosquitto is not already running -->
pgrep mosquitto
<!-- MQTT window -->
https://www.youtube.com/watch?v=72u6gIkeqUc
https://cedalo.com/blog/how-to-install-mosquitto-mqtt-broker-on-windows/
https://mosquitto.org/download/
edit file mosquitto.conf 
allow_anonymous false
listener 1883 0.0.0.0
password_file C:\Program Files\mosquitto\passwd
sudo systemctl restart mosquitto
systemctl status mosquitto.service
create file no txt
mosquitto_passwd -U passwd
net stop mosquitto
net start mosquitto
mosquitto_sub  -t "IPC|1|UNO-DM-3.3-TL-PLUS|control" -u nextwave -P 123654789 -d
<!--  -->


allow_anonymous false
#allow_anonymous true
password_file /etc/mosquitto/pwfile
listener 1883 0.0.0.0
protocol mqtt
#
listener 1884 0.0.0.0
protocol websockets
#cafile /etc/mosquitto/certs/ca.crt
#certfile /etc/mosquitto/certs/cert.pem
#keyfile /etc/mosquitto/certs/private.pem
#tls_version tlsv1
connection bridge-01
address mqtt.nextwavemonitoring.com:1883
bridge_insecure false
remote_password 123654789
remote_username admin
remote_clientid level03-line01-broker
topic # both
try_private false
<!-- MQTT Server -->
sudo nano /etc/mosquitto/conf.d/default.conf
sudo systemctl restart mosquitto
<!--  -->
connection bridge-01
address 192.168.80.230:1883
bridge_insecure false
#bridge_capath /etc/ssl/certs/
remote_password 123654789
remote_username nextwave
remote_clientid level03-line01-broker
#try_private true
#topic down/3/# in 0
#topic up/3/# out 0
#connection br-me-to-broker0
#address 192.168.80.230:1883
#remote_clientid broker0
#remote_password 123654789
#remote_username nextwave
topic # both
try_private true
<!-- MQTT Test -->
mosquitto_sub -h localhost -u nextwave -P 123654789 -t test/1 
mosquitto_pub -h localhost -u nextwave -P 123654789 -t test/1 -m 'Hello from localhost'
<!--  -->
sudo nano /etc/nginx/nginx.conf
sudo service nginx restart
http {

    server {
    listen 443 ssl;
    server_name mqtt.nextwavemonitoring.com; 
    
    ssl_certificate /etc/mosquitto/certs/cert.pem;  # certificate path
    ssl_certificate_key /etc/mosquitto/certs/private.pem; # key path   
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
        
    location /mqtt/ {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8083/mqtt/;
        #proxy_pass https://127.0.0.1:8883/mqtt/;
        #proxy_ssl_certificate  /etc/mosquitto/certs/cert.pem;  # certificate path
        #proxy_ssl_certificate_key  /etc/mosquitto/certs/private.pem; # key path 
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    }

}

<!-- Load balancer -->
http {
    upstream mqtt_server {
        server localhost:8083 weight=1;
        server localhost:8084 weight=1;
        server localhost:8085 weight=1;
    }
    server {
    listen 443 ssl;
    server_name mqtt.nextwavemonitoring.com; 
    
    ssl_certificate /etc/mosquitto/certs/cert.pem;  # certificate path
    ssl_certificate_key /etc/mosquitto/certs/private.pem; # key path   
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
        
    location /mqtt/ {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_pass http://mqtt_server;
        #proxy_pass https://mqtt_server;
        #proxy_ssl_certificate  /etc/mosquitto/certs/cert.pem;  
        #proxy_ssl_certificate_key  /etc/mosquitto/certs/private.pem;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        }
    }

}

<!-- Visual studio Code -->
https://code.visualstudio.com/#alt-downloads
sudo apt install ./code_1.67.2-1652811604_armhf.deb
<!-- Docker -->
curl -sSL https://get.docker.com | sh
https://hub.docker.com/
<!-- Container management of Docker -->
sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
http://ip-ipc:9000
<!-- Commands for docker -->
docker run -p <HostPort:containerport> imagename:tag
docker --version
docker ps
docker stop CONTAINER_ID
docker kill CONTAINER_ID
<!-- remote computer VNC -->
https://www.redhat.com/sysadmin/vnc-screen-sharing-linux
https://vinasupport.com/huong-dan-cai-dat-vnc-server-tren-ubuntu-20-04/
<!-- ssh -->
sudo apt install ufw
https://www.youtube.com/watch?v=S1FPCY8W420
sudo apt install openssh-server
sudo systemctl start ssh
sudo service ssh start
sudo systemctl status ssh
# systemctl enable ssh #enable run on startup
# systemctl start ssh #start it right now
<!-- How To Install dpkg on Kali Linux -->
sudo apt-get update
sudo apt-get -y install dpkg
<!-- remote computer TeamViewer -->
https://pimylifeup.com/raspberry-pi-teamviewer/
wget https://download.teamviewer.com/download/linux/teamviewer-host_armhf.deb
sudo dpkg -i teamviewer-host_armhf.deb
<!-- IPC -->
wget https://download.teamviewer.com/download/linux/teamviewer-host_amd64.deb
sudo dpkg -i teamviewer-host_amd64.deb
<!-- TeamViewer Allow Remote Control without Confirmation in Linux -->
https://linuxconfig.org/how-to-enable-disable-wayland-on-ubuntu-22-04-desktop
sudo nano /etc/gdm3/custom.conf
<!-- Ubuntu 20.04 shows a black screen when connecting through Teamviewer -->
sudo apt-get install xserver-xorg-video-dummy
sudo nano /usr/share/X11/xorg.conf.d/xorg.conf
and paste this (adjusting your desired resolution)
Section "Device"
    Identifier  "Configured Video Device"
    Driver      "dummy"
EndSection

Section "Monitor"
    Identifier  "Configured Monitor"
    HorizSync 31.5-48.5
    VertRefresh 50-70
EndSection

Section "Screen"
    Identifier  "Default Screen"
    Monitor     "Configured Monitor"
    Device      "Configured Video Device"
    DefaultDepth 24
    SubSection "Display"
    Depth 24
    Modes "1920x1080"
    EndSubSection
EndSection

<!-- Modbus to MQTT -->
https://qbee.io/misc/send-modbus-data-over-mqtt-using-qbee-io/
https://pypi.org/project/modbus4mqtt/
<!-- Free SFTP, SCP, S3 and FTP client for Windows -->
https://winscp.net/eng/download.php
<!-- Enhanced terminal for Windows with X11 server, tabbed SSH client, network tools and much more -->
https://mobaxterm.mobatek.net/download-home-edition.html
<!-- import mysql.connector -->
import mysql.connector
mydb = mysql.connector.connect(
host="localhost",
user="myusername",
password="mypassword",
database="mydatabase"
)
mycursor = mydb.cursor()
sql = "UPDATE books SET name = 'Web Programming in Python' WHERE id = 15"
mycursor.execute(sql)
mydb.commit()
print(mycursor.rowcount, "record(s) affected")
<!--  -->
[4, 3, 2, 1] - byteorder=Endian.Big, wordorder=Endian.Big
[3, 4, 1, 2] - byteorder=Endian.Little, wordorder=Endian.Big
[1, 2, 3, 4] - byteorder=Endian.Little, wordorder=Endian.Little
<!--  -->
python driver_of_device/ModbusTCP.py 1 "D:/NEXTWAVE/project/ipc_api"
python driver_of_device/ModbusRTU.py
python3 driver_of_device/ModbusTCP.py 1 "/home/ipc/ipc_api"
python3 /home/ipc/ipc_api/main.py
cd api_of_device
uvicorn main:app --reload
<!--  -->
sudo nano /etc/systemd/system/ipc.service
sudo nano /etc/systemd/system/reboot_message.service
ipc.service:
[Unit]
Description=Python Script Made By Me
After=multi-user.target

[Service]
RestartSec=10
Restart=always
ExecStart=usr/bin/python3 /home/ipc/ipc_api/main.py

[Install]
WantedBy=multi-user.target

sudo systemctl disable ipc.service
sudo systemctl daemon-reload
sudo systemctl enable ipc.service
sudo systemctl start ipc.service
sudo systemctl status ipc.service

<!-- Running A Python Script At Boot Using Cron -->
sudo crontab -e
@reboot sudo /usr/bin/python3 /home/ipc/ipc_api/main.py >> /var/log/ipc_api.log 2>&1

<!--  -->
1 Operation not permitted
2 No such file or directory
3 No such process
4 Interrupted system call
5 Input/output error
6 No such device or address
9 Bad file descriptor
11 Resource temporarily unavailable
12 Cannot allocate memory
13 Permission denied
16 Device or resource busy
19 No such device
23 Too many open files in system
24 Too many open files
26 Text file busy
28 No space left on device
32 Broken pipe
52 Invalid Exchange
101 Network is unreachable
110 Connection timed out
111 Connection refused
113 No route to host
129 Illegal Function (function was not allowed by the slave device)
130 Illegal Data Address (the data address is not allowed by the slave device)
131 Illegal Data Value
132 Illegal Response Length
138 Gateway Path Unavailable (the Modbus/TCP gateway may be misconfigured)
139 Device Failed to Respond (the Modbus device may be off or disconnected)
140 Received invalid Modbus data checksum
141 Received response from unexpected device
142 Received unsolicited query, assume another Modbus master device is present.
143 Modbus device probe function received some good responses and some failures.
160 Start log (Entry in log file after EMB Hub starts up)
161 Stop log (Entry in log file if EMB Hub is shut down properly)
162 System time changed, caused logger to restart logging for intervals.
163 System auto-restart
164 Log entry corrupt
<!-- Linux root -->
How do I set the root password 
sudo -i passwd
123654789

<!--  Enter password sudo -->
echo [password] | sudo ...
<!--  wmi pyuac -->
Fix IP of IPC
https://github.com/snnkbb/python-ip-changer/blob/master/ipchanger.py
https://askubuntu.com/questions/766131/how-do-i-set-a-static-ip-in-ubuntu
<!--  Get Your System Information – Using Python Script -->
https://www.geeksforgeeks.org/get-your-system-information-using-python-script/
https://www.geeksforgeeks.org/psutil-module-in-python/
https://linuxconfig.org/change-ip-address-on-ubuntu-server
sudo ifconfig -a
sudo nano etc/netplan/01-network-manager-all.yaml
<!--  ifconfig missing after Ubuntu 18.04 install -->
sudo apt install net-tools
nmcli device status
netstat -i
ifcnfig
<!-- wired device not managed  -->
sudo nano /etc/NetworkManager/NetworkManager.conf
change the line managed=false to managed=true
Save, stop and start network manager:
sudo service network-manager restart

sudo ip link set enp2s0 down --> sudo ip link set enp2s0 up
<!--  -->
sudo nano /etc/network/interfaces
auto lo enp2s0
iface lo inet loopback
<!-- Setup interface to dhcp -->
iface enp2s0 inet dhcp
<!-- efining physical interfaces such as eth0 -->
iface enp2s0 inet static
address 192.168.1.5
netmask 255.255.255.0
gateway 192.168.1.254
<!--  -->
auto enp2s0
iface enp2s0 inet static
address 192.168.0.42
network 192.168.0.0
netmask 255.255.255.0
broadcast 192.168.0.255
gateway 192.168.0.1
<!-- netplan -->
https://www.mondoze.com/guide/kb/how-to-configure-static-ip-address-on-ubuntu-18-04
sudo nano /etc/netplan/01-network-manager-all.yaml
///
<!-- use it -->
sudo nano /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp2s0:
      dhcp4: no
      addresses:
        - 192.168.121.199/24
      gateway4: 192.168.121.1
      nameservers:
          addresses: [8.8.8.8, 1.1.1.1]
network:
  version: 2
  renderer: networkd
  ethernets:
    enp2s0:
      dhcp4: yes
<!--  -->
sudo netplan apply
<!-- Permission denied Ubuntu -->
sudo chmod -R 777 /path/to/file

<!-- Visual Studio Code extensions stopped -->
Open the command palette (Ctrl + Shift + P)
Run Disable All Installed Extensions
Then run Enable All Extensions.
Restart Visual Studio Code
Ctrl + Shift +UP
Ctrl + Shift +LO
<!-- update database -->
28122023 config_type
28122023 config_information
28122023 point_list
28122023 register_block
29122023 point_list add column ->  function, value
09012023 sync_data add column -> number_of_time_retry
09012024 device_group -> name set unique
10012024 config_information -> add row "not used"
12012024 template_library -> name set unique
15012024 config_type -> add row id 16
15012024 config_information -> add row id 270 -272
15012024 device_list -> all On Update and On Delete set = Set null
15012024 device_group -> On Update and On Delete set = Set null
sysData=
{
  "id_upload_channel":1,
  "id_device":1,
  "list":[
    {"id": "2024-01-10 04:06:30","data":"'2024-02-05 04:30:00',0,0,0,0.4,222.8,222.8,4"},
    {"id": "2024-02-05 04:24:00","data":"'2024-02-05 04:30:00',0,0,0,0.4,222.8,222.8,4"},
    {"id": "2024-02-05 04:36:00","data":"'2024-02-05 04:30:00',0,0,0,0.4,222.8,222.8,4"}
  ]
}
 sudo apt install python3-netifaces

python D:\NEXTWAVE\project\ipc_api\main.py
pm2 start D:\NEXTWAVE\project\ipc_api\src/deviceDriver/ModbusTCP.py -f  --name "TCP" -- 296
pipeline {
    agent any

    stages {
        stage('Hello') {
            steps {
                checkout scmGit(branches: [[name: 'Dev-Vu']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/Eli-J-Devco/ipc_api.git']])
            }
        }
        stage('install'){
            steps{
                sh 'sudo rm -rf /sources/python/ipc_api/'
                echo 'installing libraries'
                sh 'pip3 install -r requirements.txt'
                sh 'echo 123654789 | sudo -S apt-get install python3-tk'
                sh 'echo 123654789 | sudo ufw allow 1883'
                sh 'echo 123654789 | sudo ufw allow 3000'
                sh 'echo 123654789 | sudo ufw allow 3001'
            }
        }
        stage('Build') {
            steps {
                git branch: 'Dev-Vu', url: 'https://github.com/Eli-J-Devco/ipc_api.git'
                //sh 'sudo python3 main.py'
            }
        }
        stage('product') {
            steps {
                
                //sh 'echo 123654789 | sudo cp -rf /var/lib/jenkins/workspace/ipc_api/ /sources/python/ipc_api/ '
                sh 'echo 123654789 | sudo cp -rf /var/lib/jenkins/workspace/ipc_api/ /sources/python/'
                // sh 'sudo chmod -R 777 /sources/python/ipc_api/'
                sh 'sudo python3 /sources/python/ipc_api/main.py'
            }
        }
        // stage('Build') {
        //     steps {
        //         git branch: 'Dev-Vu', url: 'https://github.com/Eli-J-Devco/ipc_api.git'
        //         sh 'pyinstaller main.spec'
                
        //     }
        // }
        //  stage('Deliver') { // (1)
        //     steps {
        //         sh "pyinstaller --onefile test/test9.py" // (2)
        //     }
        //     post {
        //         success {
        //             archiveArtifacts 'dist/test9' // (3)
        //         }
        //     }
        // }
    }
}
<!-- MQTT Topic -->
IPC/Dev
IPC/UpData
IPC/LogFile
IPC/LogDevice
<!--  -->
pm2
LogDevice
LogFile
UpData
Dev|
When Change device
call file 
sudo pm2 start /sources/python/api_python/src/deviceDriver/ModbusTCP.py --interpreter /usr/bin/python3 -f   -- 296  --restart-delay=10000
sudo pm2 start /sources/python/api_python/src/api/main.py --interpreter /usr/bin/python3 -f  --name "API"  --restart-delay=10000
sudo python3 /sources/python/api_python/src/dataSync/url.py 2
sudo python3 /sources/python/api_python/src/dataLog/file.py 2
<!-- jenkins install package app -->
You can use Python's venv like described here.
However if you really want to install packages that way, then there are a couple of solutions:
use pip's argument --break-system-packages,
add following lines to ~/.config/pip/pip.conf:
[global]
break-system-packages = true
or pip install -r requirements.txt --break-system-packages
<!--  -->

 async def get_devices(session: AsyncSession, query):
        try:
            <!-- query = select(Devices) -->
            result = await session.execute(text(query))
            devices = result.scalars().all()
            return [DeviceModel(**device.__dict__) for device in devices]
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            logger.info("Closing session")
            await session.close()