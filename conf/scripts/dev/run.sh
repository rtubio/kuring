#!/bin/bash

# Small script for executing the development server for 'kuring'.

####################
# IMPORTANT: This script is thought to be invoked from the ROOT of the project.
####################

source 'conf/project.conf'

echo "[info, $0] Starting execution, pwd = $(pwd)"

source "$VENV_ACTIVATE"
cd "$DJANGO_APP_DIR"
python manage.py migrate
python manage.py collectstatic --no-input

echo "[info, $0] Starting REDIS DOCKER (fails if it is already running, do not worry)"
docker run --name=kuring-redis --publish=6379:6379 --hostname=redis --restart=always --detach redis:alpine
echo "[info, $0] Starting INFLUXDB DOCKER (fails if it is already running, do not worry)"
docker run --name=kuring-influxdb --publish=8086:8086 --hostname=influxdb --restart=always --detach influxdb:alpine

echo "[info, $0] Starting CELERY WORKER"
celery --app kuring worker --loglevel=DEBUG

echo "[info, $0] Starting DJANGO SERVER, in DEVELOPMENT mode"
python manage.py runserver
