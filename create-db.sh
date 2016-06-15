#!/usr/bin/env bash
# This script creates the database & user specified in the environment variables from database.env.
# Note: you must connect as superuser to run this script.

# exit whole script if one command sends non-zero exit code...
set -e
# turn -x on if DEBUG is set to a non-empty string
[ -n "$DEBUG" ] && set -x
# Exit whole script when CTRL-C is sent
trap "exit" INT

# Use configured environment files and set them as shell variables
source *.env

psql -h $DB_HOST -p $DB_PORT -U postgres -c "CREATE DATABASE $DB_DATABASE WITH ENCODING='UTF8' CONNECTION LIMIT=-1;"
psql -U postgres -d template1 -c "CREATE USER $DB_USERNAME WITH PASSWORD '$DB_PASSWORD';
 GRANT ALL PRIVILEGES ON DATABASE $DB_DATABASE TO $DB_USERNAME;"

echo "[Success] Created database '$DB_DATABASE' on host '$DB_HOST' with user '$DB_USERNAME'"
