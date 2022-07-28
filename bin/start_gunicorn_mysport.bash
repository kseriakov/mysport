#!/bin/bash
source /var/www/mysport/venv/bin/activate

exec gunicorn -c "/var/www/mysport/mysport/gunicorn_config.py" mysport.wsgi
