import os
import logging
import processors
import daiquiri

DEFAULT_SETTINGS = {
    'BASE_PATH': "/home/media/",
    'DEBUG': False,
    'EXTERNAL_PREFIX': "/external/",
    'FALLBACK_SERVERS': (),
    'IMAGE_OPTIMIZATION_CMD': '',
    'NO_IMAGE_URL': "",
    'OPENCV_PREFIX': '/usr/local/share/',
    'ORIG_BASE_PATH': "/home/media/",
    'ORIG_PATH_HANDLER': None,
    'PATH_ALIASES': {},
    'SECRET_KEY': "",
    'USE_VHOSTS': False,
    'VALID_DOMAINS': [],
    'VHOST_DOC_BASE': "",
    'VALID_IMAGE_EXTENSIONS': ['jpeg', 'jpg', 'gif', 'png', ],
    'ALLOWED_PROCESSORS': ['__all__', ],
    'CHECK_SECURITY': True,
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()


def bool_from_env(key, default=False):
    try:
        if isinstance(default, bool):
            val = os.environ[key]
        else:
            val = os.environ.get(key, default)
        if val.lower() in ['true', 't', '1']:
            return True
        elif val.lower() in ['false', 'f', '0']:
            return False
        else:
            return default
    except (KeyError, ValueError):
        return default


def list_from_env(key, default=""):
    """
    Splits a string in the format "a,b,c,d,e,f" into
    ['a', 'b', 'c', 'd', 'e', 'f', ]
    """
    try:
        val = os.environ.get(key, default)
        return val.split(',')
    except (KeyError, ValueError):
        return []


def lists_from_env(key, default=""):
    """
    Splits a string in the format "a,b:c,d,e:f" into
    [('a', 'b'), ('c', 'd', 'e'), ('f', )]
    """
    try:
        val = os.environ.get(key, default)
        lists = val.split(":")
        return [i.split(',') for i in lists]
    except (KeyError, ValueError):
        return []

settings_file = os.environ.get("TRANSMOGRIFY_SETTINGS", "")

if settings_file:
    settings_mod = __import__(settings_file)
    USER_SETTINGS.update(dict([(x, getattr(settings_mod, x)) for x in dir(settings_mod) if not x.startswith("_")]))

# Shared secret
if "TRANSMOGRIFY_SECRET" in os.environ:
    USER_SETTINGS['SECRET_KEY'] = os.environ.get("TRANSMOGRIFY_SECRET")
if "TRANSMOGRIFY_SECRET_KEY" in os.environ:
    USER_SETTINGS['SECRET_KEY'] = os.environ.get("TRANSMOGRIFY_SECRET_KEY")

# Debug mode
if "TRANSMOGRIFY_DEBUG" in os.environ:
    USER_SETTINGS['DEBUG'] = bool_from_env("TRANSMOGRIFY_DEBUG")

# Document root, or vhost root if using vhosts
if "TRANSMOGRIFY_BASE_PATH" in os.environ:
    USER_SETTINGS['BASE_PATH'] = os.environ.get("TRANSMOGRIFY_BASE_PATH")

# vhosts looks for files in the combination:
#  BASE_PATH + servername + VHOST_DOC_BASE
if "TRANSMOGRIFY_USE_VHOSTS" in os.environ:
    USER_SETTINGS['USE_VHOSTS'] = bool_from_env("TRANSMOGRIFY_USE_VHOSTS", False)

# Document root under each vhost
if "TRANSMOGRIFY_VHOST_DOC_BASE" in os.environ:
    USER_SETTINGS['VHOST_DOC_BASE'] = os.environ.get("TRANSMOGRIFY_VHOST_DOC_BASE", "")

if "TRANSMOGRIFY_NO_IMG_URL" in os.environ:
    USER_SETTINGS['NO_IMAGE_URL'] = os.environ.get("TRANSMOGRIFY_NO_IMG_URL", "")

# Environment path aliases should be
if "TRANSMOGRIFY_PATH_ALIASES" in os.environ:
    USER_SETTINGS['PATH_ALIASES'] = dict(lists_from_env("TRANSMOGRIFY_PATH_ALIASES"))

# Fallback Servers
# Format is
# (regex, repl, host),
# (r"^/media/(.*), "\1", "http://www.example.com/"),
if "TRANSMOGRIFY_FAILBACK_SERVERS" in os.environ:
    try:
        USER_SETTINGS['FALLBACK_SERVERS'] = dict(lists_from_env("TRANSMOGRIFY_FALLBACK_SERVERS"))
    except (ValueError, ):
        USER_SETTINGS['FALLBACK_SERVERS'] = {}

if "TRANSMOGRIFY_ORIG_PATH_HANDLER" in os.environ:
    USER_SETTINGS['ORIG_PATH_HANDLER'] = os.environ.get("TRANSMOGRIFY_ORIG_PATH_HANDLER", "")

if "TRANSMOGRIFY_ORIG_BASE_PATH" in os.environ:
    USER_SETTINGS['ORIG_BASE_PATH'] = os.environ.get("TRANSMOGRIFY_ORIG_BASE_PATH", "/home/media/")

if "TRANSMOGRIFY_EXTERNAL_PREFIX" in os.environ:
    USER_SETTINGS['EXTERNAL_PREFIX'] = os.environ.get("TRANSMOGRIFY_EXTERNAL_PREFIX", "/external/")

if "TRANSMOGRIFY_ALLOWED_PROCESSORS" in os.environ:
    USER_SETTINGS['ALLOWED_PROCESSORS'] = os.environ.get("TRANSMOGRIFY_ALLOWED_PROCESSORS", "__all__,").split(",")

if "TRANSMOGRIFY_IMAGE_OPTIMIZATION_CMD" in os.environ:
    USER_SETTINGS['IMAGE_OPTIMIZATION_CMD'] = list_from_env("TRANSMOGRIFY_IMAGE_OPTIMIZATION_CMD")

PATH_ALIASES = {}

# Fallback Servers
FALLBACK_SERVERS = (
    # Format is
    # (regex, repl, host),
    # (r"^/media/(.*), "\1", "http://www.example.com/"),
)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)
settings_string = ["Using settings:"]
settings_string.extend(['%s: %s' % (key, val) for key, val in USER_SETTINGS.items()])
logger.info("\n".join(settings_string))


PROCESSORS = {}
ALLOW_ALL_PROCESSORS = '__all__' in USER_SETTINGS['ALLOWED_PROCESSORS']
for attr in processors.__all__:
    item = getattr(processors, attr)
    if issubclass(item, processors.Processor):
        if ALLOW_ALL_PROCESSORS or item.code in USER_SETTINGS['ALLOWED_PROCESSORS']:
            PROCESSORS[item.code()] = item

globals().update(USER_SETTINGS)
