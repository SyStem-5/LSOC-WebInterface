#!/bin/bash
#Shortcut for running a python virtual 
# environment and starting django dev server.

. set_dev_env_vars.sh

pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
pipenv run python manage.py runserver
