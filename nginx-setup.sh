#!/bin/bash
NGINX_CONFIG_PATH=${NGINX_CONFIG_PATH:-/workspaces/ebay-balance/nginx.conf}

apt-get update
DEBIAN_FRONTEND=noninteractive apt install -y nginx
rm -rf /etc/nginx/nginx.conf
ln -s "$NGINX_CONFIG_PATH" /etc/nginx/nginx.conf
mkdir /etc/nginx/logs
nginx -t
service nginx start