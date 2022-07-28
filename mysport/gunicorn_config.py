command = '/var/www/mysport/venv/bin/gunicorn'
pythonpath = '/var/www/mysport/mysport'
bind = '127.0.0.1:8002'
workers = 3
user = 'www-data'
limit_request_fields = 32000
limit_request_fieds_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=mysport.settings'
