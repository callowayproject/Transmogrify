import os
import processors

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
    'OPENCV_PREFIX': '/usr/local/share/',
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

settings_file = os.environ.get("TRANSMOGRIFY_SETTINGS", "")

if settings_file:
    settings_mod = __import__(settings_file)
    USER_SETTINGS.update(dict([(x, getattr(settings_mod, x)) for x in dir(settings_mod) if not x.startswith("_")]))

# Shared secret
if "TRANSMOGRIFY_SECRET" in os.environ:
    USER_SETTINGS['SECRET_KEY'] = os.environ.get("TRANSMOGRIFY_SECRET")

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
    USER_SETTINGS['FALLBACK_SERVERS'] = dict(lists_from_env("TRANSMOGRIFY_FAILBACK_SERVERS"))

if "TRANSMOGRIFY_ORIG_PATH_HANDLER" in os.environ:
    USER_SETTINGS['ORIG_PATH_HANDLER'] = os.environ.get("TRANSMOGRIFY_ORIG_PATH_HANDLER", "")

if "TRANSMOGRIFY_ORIG_BASE_PATH" in os.environ:
    USER_SETTINGS['ORIG_BASE_PATH'] = os.environ.get("TRANSMOGRIFY_ORIG_BASE_PATH", "/home/media/")

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

globals().update(USER_SETTINGS)
