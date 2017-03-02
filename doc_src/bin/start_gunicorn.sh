#!/bin/bash
set -e
HOMEDIR="/etc/transmogrify"
CONF="$HOMEDIR/conf/gunicorn_conf.py"
NAME=transmogrify
cd $HOMEDIR
source virtualenv/bin/activate
exec $HOMEDIR/virtualenv/bin/python gunicorn --config $CONF transmogrify.wsgi:app