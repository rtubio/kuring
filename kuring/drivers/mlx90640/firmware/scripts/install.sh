#!/bin/bash

# This script installs the streamer as a systemd service into the system.

create_streamer_conf () {
    # This function creates the configuration file for the streaming script.
    # $1 : path to the configuration file
    # $2 : FPS (default value)
    # $3 : HOST (default value)
    # $4 : PORT (default value)
  filestr=$"
FPS=$2
HOST=$3
PORT=$4
    "
  echo "$filestr" | sudo tee "$1"
}

create_systemd_conf () {
    # This function creates the configuration file for the systemd service, with the latest
    # configuration read from "conf/integration.conf"
    # $1 : path to the configuration file
    # $2 : execution command
    # $3 : working directory for the daemon
    # $4 : service identifier
    # $5 : user to run the deamon as (has the same individual group associated to)
  filestr=$"
[Unit]
Description=MLX 90640 streaming service
After=network.target

[Service]
ExecStart=$2
WorkingDirectory=$3
StandardOutput=inherited
StandardError=syslog
SyslogIdentifier=$4
Restart=always
User=$5
Group=$5
PIDFile=$6

[Install]
WantedBy=multi-user.target
    "
  echo "$filestr" | sudo tee "$1"
}

# 0) Load configuration for service creation
source "conf/integration.conf"

# 1) Create system user, should create directories all along
[[ -z $( cat "/etc/passwd" | cut -d':' -f1 | grep "$SERVICE_USER" ) ]] && {
    sudo useradd -s /usr/sbin/nologin -r -m -d "$SERVICE_WORKINGDIR" "$SERVICE_USER"
} || {
    echo "[$0] User <$SERVICE_USER> exists, skipping..."
}

# 2) Copy binary file to executable destination
[[ ! -f "$SERVICE_BINARY" ]] && {
    sudo cp -f "$BINARY_PATH" "$SERVICE_BINARY"
    sudo chown "$SERVICE_USER:$SERVICE_USER" "$SERVICE_BINARY"
    sudo chmod ug+x "$SERVICE_BINARY"
} || {
    echo "[$0] File <$SERVICE_BINARY> exists, skipping..."
}

[[ ! -f "$STREAMER_BINARY" ]] && {
    sudo cp -f "$STREAMER_PATH" "$STREAMER_BINARY"
    sudo chown "$SERVICE_USER:$SERVICE_USER" "$STREAMER_BINARY"
    sudo chmod ug+x "$STREAMER_BINARY"
} || {
    echo "[$0] File <$STREAMER_BINARY> exists, skipping..."
}

# 3) Create configuration streamer
[[ ! -f "$streamer_conf" ]] && {
    create_streamer_conf "$streamer_conf" "$FPS" "$REMOTE_HOST" "$REMOTE_PORT"
} || {
    echo "[$0] Streamer configuration file <$streamer_conf> exists, skipping..."
}

# 4) Configure systemd
[[ ! -f "$systemd_service_conf" ]] && {

    create_systemd_conf "$systemd_service_conf" \
        "$SERVICE_EXEC" "$SERVICE_WORKINGDIR" "$SERVICE_ID" "$SYSTEMD_USER" "$SERVICE_PID"

    sudo systemctl daemon-reload && \
        sudo systemctl enable "$SERVICE_NAME" && \
        sudo systemctl start "$SERVICE_NAME"

} || {
    echo "[$0] Systemd configuration file <$systemd_service_conf> exists, skipping..."
}
