#!/usr/bin/bash

cat > webtech.service << END
# /etc/systemd/system/helloapp.service
[Unit]
Description=server
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/$USER/train_site
ExecStart=/home/$USER/train_site/env/bin/waitress-serve --listen=127.0.0.1:5000 server_file_name:app 
Restart=always

[Install]
WantedBy=multi-user.target
END
