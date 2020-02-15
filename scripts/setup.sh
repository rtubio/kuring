#!/bin/bash
#
# Small script for the installation of the dependencies required for creating the DEVELOPMENT environment.
#
# >>> IMPORTANT <<< This script is thought to be invoked from the ROOT of the project.
#
# @author: ricardo@karbontek.co.jp


add_extra_repositories () {
  # docker repository
  sudo apt update
  sudo apt install curl
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
  sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable"
  sudo apt update
  apt-cache policy docker-ce
}


post_sys_install () {
  sudo usermod -aG docker "$USER"
  # TODO # this needs to be manually executed: su - ${USER}
}


create_django_secret () {
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


install_redis () {
  # This function installs REDIS server using the docker image - no need for extra configuration.
  docker run --name=kuring-redis --publish=6379:6379 --hostname=redis --restart=always --detach redis:alpine
}


create_influxdb_secret () {
  # Creates the secrets file for the InfluxDB/Django configuration
  # $1 : path to the secrets file to be created
  # $2 : password for the administrator user
  # $3 : name for the regular user
  # $4 : password for the regular user
  # $5 : name for the new database to be created
  filestr=$"
{
  \"admp\": \"$2\",
  \"usrn\": \"$3\",
  \"usrp\": \"$4\",
  \"dbnx\": \"$5\"
}"
  echo "$filestr" > "$1"
}


install_influxdb () {
  # This function installs InfluxDB locally using docker and configures it with the same data than Django.
  # docker run --name=kuring-influxdb --publish=8086:8086 --hostname=influxdb --restart=always --detach influxdb:alpine

  echo -n "Please input the name for the InfluxDB database:"
  read dbname

  echo -n 'Please input password for the admin InfluxDB database user:'
  read -s password
  echo
  echo -n 'Please input your password again:'
  read -s password2
  echo

  [[ "$password" == "$password2" ]] || {
    echo 'Passwords do not match, please execute again...'
    exit -1
  }
  admpass="$password"

  echo -n "Please input the name for the InfluxDB user:"
  read usrname

  echo -n "Please input password for the <$idbname> InfluxDB database user:"
  read -s password
  echo
  echo -n 'Please input your password again:'
  read -s password2
  echo

  [[ "$password" == "$password2" ]] || {
    echo 'Passwords do not match, please execute again...'
    exit -1
  }
  usrpass="$password"

  echo "dbname=$dbname,admpass=$admpass,usrname=$usrname,usrpass=$usrpass"

  docker run \
      -e INFLUXDB_HTTP_AUTH_ENABLED=true\
      -e INFLUXDB_ADMIN_USER=admin -e INFLUXDB_ADMIN_PASSWORD="$admpass" \
      --name=kuring-influxdb --publish=8086:8086 --hostname=influxdb --restart=always --detach \
      influxdb:alpine

  docker run --name=kuring-influxui --publish=9999:80 --restart=always --detach sillydong/influxdb-ui

# NOTE # It was not possible to make the configuration of InfluxDB using the recommended script included within the
# docker image. The process has been altered and that script has been replaced by a Python script.
#     # The commands are kept below for further reference.
#     # Instructions taken from:
#             https://hub.docker.com/_/influxdb/
#     # Python script configuration taken from:
#     #       https://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdbclient

#  docker run \
#      -e INFLUXDB_HTTP_AUTH_ENABLED=true\
#      -e INFLUXDB_ADMIN_USER=admin -e INFLUXDB_ADMIN_PASSWORD="$admpass" \
#      -e INFLUXDB_USER="$usrname" -e INFLUXDB_USER_PASSWORD="$usrpass" \
#      -e INFLUXDB_DB="$dbname" \
#      --name=kuring-influxdb --publish=8086:8086 --hostname=influxdb --restart=always --detach \
#      influxdb:alpine /init-influxdb.sh
# docker run -e INFLUXDB_HTTP_AUTH_ENABLED=true --name=kuring-influxdb \
# --publish=8086:8086 --hostname=influxdb --restart=always --detach \
# influxdb:alpine /init-influxdb.sh
# docker exec kuring-influxdb /init-influxdb.sh
# docker exec kuring-influxdb influxd config > /tmp/influxdb.conf

  python "$influxdb_py" "$dbname" "$usrname" "$usrpass" "admin" "$admpass"

  create_influxdb_secret "$SECRETS_INFLUXDB" "$admpass" "$usrname" "$usrpass" "$dbname"

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


install_django () {
  source "$VENV_ACTIVATE"
  # 4.1) create secret key
  key="$( python $django_skg )"
  create_django_secret "$SECRETS_DJANGO" "$key"
  # 4.2) migrate the database and create superuser (DEVELOPMENT)
  cd "$DJANGO_APP_DIR"
  python manage.py makemigrations && python manage.py migrate
  python manage.py createsuperuser
  python manage.py collectstatic --no-input
  cd ..
}


source 'config/scripts.config'

echo "[info, $0] Starting execution (DEV ENVIRONMENT SETUP), pwd = $(pwd)"
export __DJ_DEVPROD='dev'

# 0) Create required directories for DEVELOPMENT
mkdir -p "$SECRETS_DIR"
mkdir -p "$STATIC_DIR"
# TODO # Remove if unnecessary: # mkdir -p "$CELERY_LOGS"

# 1) Install Debian packages for DEVELOPMENT
add_extra_repositories
install_sys_packages
post_sys_install

# 2) Setup Python and Javascript environments
install_env_packages
npm install

# 3) Setup Django
install_django

# 4) Setup influxDB and REDIS
install_influxdb
install_redis

# 5) Restore environment and leave
deactivate
