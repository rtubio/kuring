#!/bin/bash

# Small script to configure the database and the user for the 'kuring' server


create_sql () {
  # Creates a file with the SQL commands to be executed
  # $1 : string with the path to the file where the SQL commands are stored
  # $2 : string with the password for the new user to be created

  filestr=$"
CREATE DATABASE '$DBNAME';
CREATE USER '$DBUSER' WITH PASSWORD '$2';
ALTER ROLE '$DBUSER' SET client_encoding TO 'utf8';
ALTER ROLE '$DBUSER' SET default_transaction_isolation TO 'read committed';
ALTER ROLE '$DBUSER' SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE '$DBNAME' TO '$DBUSER';
  "
  echo "$filestr" > "$1"

}


source "config/scripts.config"
source "config/sql.config"
source "$django_db_sh"

echo -n 'Please input password for the new MySQL database user:'
read -s password
echo
echo -n 'Please input your password again:'
read -s password2
echo

[[ "$password" == "$password2" ]] && {
  echo 'Passwords match, proceeding with the setup of the database'
  create_sql "$sql_file" "$password"
  echo 'Please input your <root> password to access the database console:'
  sudo psql "$DBNAME" -f "$sql_file"
  echo 'Creating the MYSQL JSON configuration for Django'
  create_django_config "$SECRETS_DB" "$password"
} || {
  echo 'Passwords do not match, please execute again...'
}
