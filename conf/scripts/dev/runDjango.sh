#!/bin/bash

source 'conf/project.conf'
source "$VENV_ACTIVATE"
export PYTHONPATH="$PYTHONPATH:$XPYTHON_PATH_D"

export __DJ_DEVPROD='dev' && cd kuring && clear && \
  python manage.py makemigrations && \
  python manage.py migrate && \
  python manage.py collectstatic --no-input && \
  python manage.py runserver

deactivate
