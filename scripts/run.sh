#!/bin/bash

# Small script for executing the development server for 'kuring'.

####################
# IMPORTANT: This script is thought to be invoked from the ROOT of the project.
####################
source 'config/scripts.config'

echo "[info, $0] Starting execution, pwd = $(pwd)"

source "$VENV_ACTIVATE"
cd "$DJANGO_APP_DIR"
python manage.py migrate
python manage.py collectstatic --no-input

echo "[info, $0] Starting REDIS DOCKER (fails if it is already running, do not worry)"
docker run --name=kuring-redis --publish=6379:6379 --hostname=redis --restart=on-failure --detach redis:latest

echo "[info, $0] Starting CELERY WORKER"
export __DJ_DEVPROD='dev' && celery --app kuring worker -l info

echo "[info, $0] Starting DJANGO SERVER, in DEVELOPMENT mode"
python manage.py runserver
