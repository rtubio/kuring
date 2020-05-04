#!/bin/bash

source 'conf/project.conf'
loglevel='DEBUG'
[[ "$#" -eq '1' ]] && loglevel="$1"

source "$VENV_ACTIVATE"
export PYTHONPATH="$PYTHONPATH:$XPYTHON_PATH_D"

export __DJ_DEVPROD='dev' && cd kuring && clear && \
  celery -A kuring worker -E --loglevel="$loglevel"

deactivate
