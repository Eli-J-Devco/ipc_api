# scada
<!-- Language Python -->
sudo apt-get update
sudo apt-get install python
pip --version
sudo apt-get install pip
<!-- Project -->
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
<!-- Nodejs -->
curl -sSL https://deb.nodesource.com/setup_14.x | sudo bash -
sudo apt install -y nodejs
<!-- Process Management -->
https://pm2.keymetrics.io/docs/usage/quick-start/
npm install pm2@latest
<!-- Database -->
https://blog.hostvn.net/chia-se/huong-dan-cai-dat-mysql-tren-ubuntu-20.html
sudo apt install mysql-server
mysql -u username -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';

DROP USER 'root'@'localhost';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON * . * TO 'root'@'%';

<!-- MQTT -->
https://www.vultr.com/docs/install-mosquitto-mqtt-broker-on-ubuntu-20-04-server/
sudo apt update 
sudo apt install -y mosquitto
<!-- Secure the Mosquitto Server -->

<!-- Visual studio Code -->
https://code.visualstudio.com/#alt-downloads
sudo apt install ./code_1.67.2-1652811604_armhf.deb
<!-- Docker -->
curl -sSL https://get.docker.com | sh
docker --version
<!-- Container management of Docker -->
sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latesthttp://http://http://http://ip-ipc:9000
<!-- remote computer VNC -->
https://www.redhat.com/sysadmin/vnc-screen-sharing-linux
https://vinasupport.com/huong-dan-cai-dat-vnc-server-tren-ubuntu-20-04/
<!-- remote computer TeamViewer -->
https://pimylifeup.com/raspberry-pi-teamviewer/
wget https://download.teamviewer.com/download/linux/teamviewer-host_armhf.deb
sudo dpkg -i teamviewer-host_armhf.deb