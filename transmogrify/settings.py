import os
import processors
import warnings

DEFAULT_SETTINGS = {
    'SECRET_KEY': "",
    'DEBUG': False,
    'ORIG_PATH_HANDLER': None,
    'ORIG_BASE_PATH': "/home/media/",
    'USE_VHOSTS': False,
    'BASE_PATH': "/home/media/",
    'VHOST_DOC_BASE': "",
    'NO_IMAGE_URL': "",
    'PATH_ALIASES': {},
    'FALLBACK_SERVERS': (),
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()


def bool_from_env(key, default=False):
    try:
        val = os.environ[key]
        if val.lower() in ['true', 't', '1']:
            return True
        elif val.lower() in ['false', 'f', '0']:
            return False
        else:
            return default
    except (KeyError, ValueError):
        return default

def lists_from_env(key):
    """
    Splits a string in the format "a,b:c,d,e:f" into
    [('a', 'b'), ('c', 'd', 'e'), ('f', )]
    """
    try:
        val = os.environ[key]
        lists = val.split(":")
        return [i.split(',') for i in lists]
    except (KeyError, ValueError):
        return ()

try:
    from django.conf import settings
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

if HAS_DJANGO:
    ERR_MSG = "settings.%s is deprecated; use settings.TRANSMOGRIFY_SETTINGS instead."

    SECRET_KEY = getattr(settings, "TRANSMOGRIFY_SECRET", None)
    if SECRET_KEY is None:
        USER_SETTINGS['SECRET_KEY'] = SECRET_KEY
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_SECRET', DeprecationWarning)

    # Debug mode
    DEBUG = getattr(settings, "TRANSMOGRIFY_DEBUG", None)
    if DEBUG is None:
        USER_SETTINGS['DEBUG'] = DEBUG
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_DEBUG', DeprecationWarning)

    # Document root, or vhost root if using vhosts
    BASE_PATH = getattr(settings, "TRANSMOGRIFY_BASE_PATH", None)
    if BASE_PATH is None:
        USER_SETTINGS['BASE_PATH'] = BASE_PATH
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_BASE_PATH', DeprecationWarning)

    # vhosts looks for files in the combination:
    #  BASE_PATH + servername + VHOST_DOC_BASE
    USE_VHOSTS = getattr(settings, "TRANSMOGRIFY_USE_VHOSTS", None)
    if USE_VHOSTS is None:
        USER_SETTINGS['USE_VHOSTS'] = USE_VHOSTS
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_USE_VHOSTS', DeprecationWarning)

    # Document root under each vhost
    VHOST_DOC_BASE = getattr(settings, "TRANSMOGRIFY_VHOST_DOC_BASE", None)
    if VHOST_DOC_BASE is None:
        USER_SETTINGS['VHOST_DOC_BASE'] = VHOST_DOC_BASE
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_VHOST_DOC_BASE', DeprecationWarning)

    NO_IMAGE_URL = getattr(settings, "TRANSMOGRIFY_NO_IMG_URL", None)
    if NO_IMAGE_URL is None:
        USER_SETTINGS['NO_IMAGE_URL'] = NO_IMAGE_URL
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_NO_IMAGE_URL', DeprecationWarning)

    # A dictionary of URL paths to real paths
    # e.g. {'/media/': '/assets/'} would change a request like
    # /media/images/spanish_inquisition.png
    # to
    # /assets/images/spanish_inquisition.png
    # The changed request path is then added to BASE_PATH for original file
    # location
    PATH_ALIASES = getattr(settings, "TRANSMOGRIFY_PATH_ALIASES", None)
    if PATH_ALIASES is None:
        USER_SETTINGS['PATH_ALIASES'] = PATH_ALIASES
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_PATH_ALIASES', DeprecationWarning)

    FALLBACK_SERVERS = getattr(settings, "TRANSMOGRIFY_FALLBACK_SERVERS", "")
    if PATH_ALIASES is None:
        USER_SETTINGS['FALLBACK_SERVERS'] = FALLBACK_SERVERS
        warnings.warn(ERR_MSG % 'TRANSMOGRIFY_FALLBACK_SERVERS', DeprecationWarning)

else:
    # Shared secret
    USER_SETTINGS['SECRET_KEY'] = os.environ.get("TRANSMOGRIFY_SECRET", "")

    # Debug mode
    USER_SETTINGS['DEBUG'] = bool_from_env("TRANSMOGRIFY_DEBUG", False)

    # Document root, or vhost root if using vhosts
    USER_SETTINGS['BASE_PATH'] = os.environ.get("TRANSMOGRIFY_BASE_PATH", "/home/media/")

    # vhosts looks for files in the combination:
    #  BASE_PATH + servername + VHOST_DOC_BASE
    USER_SETTINGS['USE_VHOSTS'] = bool_from_env("TRANSMOGRIFY_USE_VHOSTS", False)

    # Document root under each vhost
    USER_SETTINGS['VHOST_DOC_BASE'] = os.environ.get("TRANSMOGRIFY_VHOST_DOC_BASE", "")

    USER_SETTINGS['NO_IMAGE_URL'] = os.environ.get("TRANSMOGRIFY_NO_IMG_URL", "")

    # Environment path aliases should be
    USER_SETTINGS['PATH_ALIASES'] = dict(lists_from_env("TRANSMOGRIFY_PATH_ALIASES"))

    # Fallback Servers
    # Format is
    # (regex, repl, host),
    # (r"^/media/(.*), "\1", "http://www.example.com/"),
    USER_SETTINGS['FALLBACK_SERVERS'] = dict(lists_from_env("TRANSMOGRIFY_FAILBACK_SERVERS"))

    USER_SETTINGS['ORIG_PATH_HANDLER'] = os.environ.get("TRANSMOGRIFY_ORIG_PATH_HANDLER", "")
    USER_SETTINGS['ORIG_BASE_PATH'] = os.environ.get("TRANSMOGRIFY_ORIG_BASE_PATH", "/home/media/")


PROCESSORS = {}
for attr in processors.__all__:
    item = getattr(processors, attr)
    if issubclass(item, processors.Processor):
        PROCESSORS[item.code()] = item

globals().update(USER_SETTINGS)
