sudo apt-get update
sudo apt install -y nginx
sudo rm -rf /etc/nginx/nginx.conf
sudo ln -s /workspaces/python/nginx.conf /etc/nginx/nginx.conf
sudo service nginx start