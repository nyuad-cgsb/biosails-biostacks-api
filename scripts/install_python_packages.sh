#!/usr/bin/env bash

set -x -e

echo "No packages to install"
#find /home/airflow/pkgs -maxdepth 1 -mindepth 1 -type d | xargs -I {} "cd {} && pip --ignore-installed install ."
#cd /root/pkgs/nyuad-cgsb-jira-client
#pip install --ignore-installed .
