# scada
<!-- Language Python -->
sudo apt-get update
sudo apt-get install python
pip --version
sudo apt-get install pip
<!-- Nodejs -->
curl -sSL https://deb.nodesource.com/setup_14.x | sudo bash -
<!-- Process Management -->
https://pm2.keymetrics.io/docs/usage/quick-start/
npm install pm2@latest
<!-- Database -->
sudo apt install mysql-server
mysql -u username -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';

DROP USER 'root'@'localhost';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON * . * TO 'root'@'%';

<!-- Project -->
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt


<!-- Visual studio Code -->
https://code.visualstudio.com/#alt-downloads
sudo apt install ./code_1.67.2-1652811604_armhf.deb
<!-- Docker -->
curl -sSL https://get.docker.com | sh
docker --version
<!-- Container management of Docker -->
sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latesthttp://http://http://http://ip-ipc:9000