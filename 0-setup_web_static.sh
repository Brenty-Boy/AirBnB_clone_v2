#!/usr/bin/env bash
# sets up the web servers for the deployment of web_static

# update the package lists
sudo apt-get -y update

# install nginx
sudo apt-get -y install nginx

# make directories for the deployment using -p to create all parent directories if not existing
sudo mkdir -p /data/web_static/releases/test 
sudo mkdir -p /data/web_static/shared

# give ownership of the /data/ directory to the ubuntu user 
sudo chown -R ubuntu /data/

# give group ownership of the /data/ directory to the ubuntu user
sudo chgrp -R ubuntu /data/

# create a test HTML file
echo "This is a Test-Page!" > /data/web_static/releases/test/index.html

# create a symbolic link to the test HTML file
#---'ln -s' creates a symbolic link
#---'f' forces the symbolic link to be created if the target already exists, hence overwriting whenever target file is updated
sudo ln -sf /data/web_static/releases/test/ /data/web_static/current

# server name not specified
# listen to port 80
# [::] listens to IPv6 connections
# add_header adds a header to the response indicating the server name $HOSTNAME
# root is the root directory of the server where nginx will look for files to serve
# index is the default file that nginx will serve if no file is specified in the URL
# location is the path to the content to be served '/hbnb_static' path to url - https://mydomain.com/hbnb_static
# alias is the path to the content to be served '/data/web_static/current'. check how to use 'root' and 'alias' in nginx
# return 301 redirects the client to another URL
# error_page 404 is the path to the custom 404 page
# internal is used to prevent nginx from serving the page to the client
printf %s "server {
    listen 80 default_server;
    listen [::]:80 default_server;
    add_header X-Served-By $HOSTNAME;
    root   /var/www/html;
    index  index.html index.htm index.nginx-debian.html;

    location /hbnb_static {
        alias /data/web_static/current;
        index index.html index.htm index.nginx-debian.html 8-index.html;
    }

    location /redirect_me {
        return 301 https://google.com;
    }

    error_page 404 /error_404.html;
    location /404 {
      root /var/www/html;
      internal;
    }
}" > /etc/nginx/sites-available/default

sudo service nginx restart
