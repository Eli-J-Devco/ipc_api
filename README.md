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
<!-- install all package python -->
pip install -r requirements.txt
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
<!-- Secure the Mosquitto Server -->
<!-- Tester client publish/Subscribe -->
https://mqtt-explorer.com/
<!-- MQTT window -->
https://www.youtube.com/watch?v=72u6gIkeqUc
https://cedalo.com/blog/how-to-install-mosquitto-mqtt-broker-on-windows/
https://mosquitto.org/download/
edit file mosquitto.conf 
allow_anonymous false
listener 1883 0.0.0.0
password_file C:\Program Files\mosquitto\passwd

create file no txt
mosquitto_passwd -U passwd
net stop mosquitto
net start mosquitto
mosquitto_sub  -t "IPC|1|UNO-DM-3.3-TL-PLUS|control" -u nextwave -P 123654789 -d
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

<!-- update database -->
28122023 config_type
28122023 config_information
28122023 point_list
28122023 register_block
