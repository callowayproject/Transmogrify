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

PROCESSORS = {}
for attr in processors.__all__:
    item = getattr(processors, attr)
    if issubclass(item, processors.Processor):
        PROCESSORS[item.code()] = item