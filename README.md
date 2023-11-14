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
<!-- FastAPI -->
https://fastapi.tiangolo.com/
<!-- Run a Server Manually - Uvicorn -->
uvicorn main:app --host 0.0.0.0 --port 8000
<!-- Run a Server Manually - Uvicorn and auto reload -->
uvicorn main:app --reload
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
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';

DROP USER 'ipc'@'%';
DROP USER 'root'@'localhost';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123654789';
CREATE USER 'ipc'@'%' IDENTIFIED WITH mysql_native_password BY '@$123654789';
CREATE USER 'ipc'@'%' IDENTIFIED  BY '@$123654789';
GRANT ALL PRIVILEGES ON * . * TO 'ipc'@'%';
SELECT User, Host, Password FROM mysql.user;

<!-- Your password does not satisfy the current policy requirements -->
SHOW VARIABLES LIKE 'validate_password%';
SET GLOBAL validate_password.length = 4;
SET GLOBAL validate_password.policy=LOW;
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
create file no txt
mosquitto_passwd -U passwd
net stop mosquitto
net start mosquitto
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