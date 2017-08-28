import os
APP = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "transmogrify",
]
TRANSMOGRIFY_SECRET = "whatevs"

os.environ['TRANSMOGRIFY_SECRET'] = TRANSMOGRIFY_SECRET
os.environ['TRANSMOGRIFY_ORIG_BASE_PATH'] = os.path.join(APP, "transmogrify", "testdata")
os.environ['TRANSMOGRIFY_BASE_PATH'] = os.path.join(APP, "transmogrify", "testdata")
os.environ['TRANSMOGRIFY_PATH_ALIASES'] = '/media/,/'
