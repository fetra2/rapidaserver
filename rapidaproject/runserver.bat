@echo off
start "" "python" "C:\inetpub\wwwroot\rapida\rapidaproject\runserver.py" &
::cmd /k "waitress-serve" "--port=808 rapidaproject.wsgi:application"
::pause
