import os, sys, site
import django.core.handlers.wsgi

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
site.addsitedir('/Users/coordt/.virtualenvs/transmogrify/lib/python2.6/site-packages')

application = django.core.handlers.wsgi.WSGIHandler()