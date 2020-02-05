#!/bin/bash
#
# Small script for the installation of the dependencies required for creating the DEVELOPMENT environment.
#
# >>> IMPORTANT <<< This script is thought to be invoked from the ROOT of the project.
#
# @author: ricardo@karbontek.co.jp

create_django_secret() {
  # Creates the secrets file for Django with the given key
  # $1 : path to the secrets file to be created
  # $2 : secret key to be stored

  filestr=$"
{
  \"djsk\": \"$2\"
}
  "
  echo "$filestr" > "$1"

}

install_sys_packages () {
  [[ -f "$PACKAGES_FILE" ]] && {
    sudo apt update && sudo apt -y full-upgrade
    sudo apt -y install $(grep -vE "^\s*#" "$PACKAGES_FILE" | tr "\n" " ")
  } || {
    echo "[warn, $0] No \"$PACKAGES_FILE\" available, skipping SYS package installation..."
  }
}

install_env_packages () {
  [[ ! -d "$VENV_DIR" ]] && virtualenv --python=python3 "$VENV_DIR" && echo "[info, $0] \"$VENV_DIR\" initialized"
  [[ -f "$REQUIREMENTS_FILE" ]] && {
    source "$VENV_ACTIVATE"
    pip install -r "$REQUIREMENTS_FILE"
    deactivate
  } || {
    echo "[warn, $0] No \"$REQUIREMENTS_FILE\" available, skipping VENV package installation..."
  }
}


source 'config/scripts.config'

echo "[info, $0] Starting execution, pwd = $(pwd)"

# 0) Create required directories for DEVELOPMENT
mkdir -p "$SECRETS_DIR"
mkdir -p "$STATIC_DIR"
# TODO # Remove if unnecessary: # mkdir -p "$CELERY_LOGS"

# 1) Install Debian packages for DEVELOPMENT
install_sys_packages
# 2) Setup virtual environment for DEVELOPMENT
install_env_packages

# 3) Configure Django
source "$VENV_ACTIVATE"
# 3.1) create secret key
key="$( python $django_skg )"
create_secret "$SECRETS_DJANGO" "$key"
# 3.2) migrate the database and create superuser (DEVELOPMENT)
cd "$DJANGO_APP_DIR"
python manage.py migrate dev
python manage.py createsuperuser dev
python manage.py collectstatic --no-input dev
cd ..

deactivate
