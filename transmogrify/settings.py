from PIL import ImageFilter
import os, re
import processors

try:
    from django.conf import settings
    HAS_DJANGO=True
except ImportError:
    HAS_DJANGO=False

if HAS_DJANGO:
    from django.conf import settings

    SECRET_KEY = getattr(settings, "TRANSMOGRIFY_SECRET", "")

    # Debug mode
    DEBUG = getattr(settings, "TRANSMOGRIFY_DEBUG", True)

    # Document root, or vhost root if using vhosts
    BASE_PATH = getattr(settings, "TRANSMOGRIFY_BASE_PATH","/home/media/")

    # vhosts looks for files in the combination:
    #  BASE_PATH + servername + VHOST_DOC_BASE
    USE_VHOSTS = getattr(settings, "TRANSMOGRIFY_USE_VHOSTS", False)

    # Document root under each vhost
    VHOST_DOC_BASE = getattr(settings, "TRANSMOGRIFY_VHOST_DOC_BASE", "")

    NO_IMAGE_URL = getattr(settings, "TRANSMOGRIFY_NO_IMG_URL", "")
    
    # A dictionary of URL paths to real paths
    # e.g. {'/media/': '/assets/'} would change a request like
    # /media/images/spanish_inquisition.png
    # to
    # /assets/images/spanish_inquisition.png
    # The changed request path is then added to BASE_PATH for original file
    # location
    PATH_ALIASES = getattr(settings, "TRANSMOGRIFY_PATH_ALIASES", {})

    FALLBACK_SERVERS = getattr(settings, "TRANSMOGRIFY_FALLBACK_SERVERS", "")
else:
    # Shared secret
    SECRET_KEY = os.environ.get("TRANSMOGRIFY_SECRET", "")

    # Debug mode
    DEBUG = os.environ.get("TRANSMOGRIFY_DEBUG", True)

    # Document root, or vhost root if using vhosts
    BASE_PATH = os.environ.get("TRANSMOGRIFY_BASE_PATH","/home/media/")

    # vhosts looks for files in the combination:
    #  BASE_PATH + servername + VHOST_DOC_BASE
    USE_VHOSTS = os.environ.get("TRANSMOGRIFY_USE_VHOSTS", False)

    # Document root under each vhost
    VHOST_DOC_BASE = os.environ.get("TRANSMOGRIFY_VHOST_DOC_BASE", "")

    NO_IMAGE_URL = os.environ.get("TRANSMOGRIFY_NO_IMG_URL", "")

    PATH_ALIASES = {}

    # Fallback Servers 
    FALLBACK_SERVERS = (
        # Format is 
        # (regex, repl, host), 
        # (r"^/media/(.*), "\1", "http://www.example.com/"),
        )

PROCESSORS = {}
for attr in processors.__all__:
    item = getattr(processors, attr)
    if issubclass(item, processors.Processor):
        PROCESSORS[item.code()] = item
