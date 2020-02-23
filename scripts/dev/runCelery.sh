#!/bin/bash

loglevel='DEBUG'
[[ "$#" -eq '1' ]] && loglevel="$1"

source ".env/bin/activate"

export __DJ_DEVPROD='dev' && cd kuring && clear && \
  celery -A kuring worker -E --loglevel="$loglevel"

deactivate
