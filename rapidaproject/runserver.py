from waitress import serve
from rapidaproject.wsgi import application
serve(application, host='0.0.0.0', port=8041)
#waitress-serve --port=8041 rapidaproject.wsgi:application