#!/bin/bash

export DJANGO_ALLOW_ASYNC_UNSAFE="true"
export SECRETS_LOCATION="/run/secrets"
export SECRET_KEY="mehsecretkey_bleh"
export REDIS_HOST="127.0.0.1"
export REDIS_PORT=6379
export SQL_ENGINE="django.db.backends.postgresql"
export SQL_DATABASE="lsoc_web_interface"
export SQL_USER="postgres"
export SQL_PASSWORD="Thisismylongtestpassword_1"
export SQL_HOST="127.0.0.1"
export SQL_PORT="5432"
