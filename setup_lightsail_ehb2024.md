Setup lightsail instance
------------------------

Ubuntu 512 MB RAM, 2 vCPUs, 20 GB SSD

IPv4 and IPv6 firewall:
open ports 22, 80 and 443

Connect to static public IPv4 address

Add A and AAAA entries to domain records


Install python and setup app
----------------------------

~~~
sudo apt update
sudo apt install build-essential python3.10-dev python3.10-venv libssl-dev
python3 -mvenv venv
source venv/bin/activate
pip install wheel
pip install Pillow
pip install qrcode
pip install flask-socketio
pip install gevent-websocket
pip install termcolor

export UWSGI_PROFILE_OVERRIDE=ssl=true
pip install -I --no-binary=:all: --no-cache-dir uwsgi
mkdir -p logs
~~~

Copy sources to the server at /home/ubuntu/

~~~
# /home/ubuntu/dancecards.ini
[uwsgi]
http-socket = :5000
gevent = 1000
http-websockets = true
master = true
processes = 1
wsgi-file = dancecards.py
callable = app
vacuum = true
die-on-term = true
disable-logging = true
log-5xx = true
logto = /home/ubuntu/logs/dancecards.log
~~~

~~~
# /etc/systemd/system/dancecards.service
[Unit]
Description=uWSGI instance to serve dancecards
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/
Environment="PATH=/home/ubuntu/venv/bin"
ExecStart=/home/ubuntu/venv/bin/uwsgi --ini dancecards.ini

[Install]
WantedBy=multi-user.target
~~~

nginx
-----

~~~
sudo apt install nginx
~~~

~~~
# /etc/nginx/sites-enabled/dancecards.conf
server {
        server_name dancecards.europeanharmonybrigade.org;
        listen 80;
        listen [::]:80;

location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000/;
        client_max_body_size 10M;
}

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
}
~~~

Use certbot to request and setup SSL:

~~~bash
sudo snap install --classic certbot
sudo certbot --nginx
~~~


Backup
------

Add cronjob:
~~~
0 *  *   *   *     /home/ubuntu/backup.sh
~~~

~~~bash
#!/bin/bash
date=$(date +%F-%H-%M)
for i in /home/ubuntu/*.db; do
        name=$(basename $i)
        cp $i /home/ubuntu/backup/${date}_${name}
done
~~~


