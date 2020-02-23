#!/bin/bash

source .env/bin/activate

export __DJ_DEVPROD='dev' && cd kuring && clear && \
  python manage.py makemigrations && \
  python manage.py migrate && \
  python manage.py collectstatic --no-input && \
  python manage.py runserver

deactivate
