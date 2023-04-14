"""Gunicorn *production* config file"""

import multiprocessing

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "rapidaproject.wsgi:application"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
# The socket to bind
bind = "127.0.0.1:5000"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False