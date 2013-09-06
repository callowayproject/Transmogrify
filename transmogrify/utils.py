"""
1. Get url like:

   img/photos/2008/05/12/WIZARDS_0034_05022035_r329x151.jpg?e315d4515574cec417b1845392ba687dd98c17ce

2. Parse url into:

    action_string: r329x151
    parent_dir:    img/photos/2008/05/12/
    ext:           jpg
    base_filename: WIZARDS_0034_05022035
    security_hash: e315d4515574cec417b1845392ba687dd98c17ce
    requested_path /path/to/media_root/img/photos/2008/05/12/WIZARDS_0034_05022035_r329x151.jpg

3. Verify security hash:

    sha1(action_string + KEY).hexdigest = security_hash

5. Return
"""
import os
import re
import urllib
import urlparse
from hashlib import sha1
from settings import (BASE_PATH, USE_VHOSTS, VHOST_DOC_BASE, PROCESSORS,
                      SECRET_KEY, PATH_ALIASES, DEBUG, ORIG_BASE_PATH)


class Http404(Exception):
    pass


def is_valid_actionstring(action_string):
    code, arg = action_string[0], action_string[1:]

    return code in PROCESSORS and PROCESSORS[code].param_pattern().match(arg)


def create_securityhash(action_tuples):
    """
    Create a SHA1 hash based on the KEY and action string
    """
    action_string = "".join(["_%s%s" % a for a in action_tuples])
    security_hash = sha1(action_string + SECRET_KEY).hexdigest()
    return security_hash


def generate_url(url, action_string):
    security_hash = sha1(action_string + SECRET_KEY).hexdigest()
    base_url, ext = os.path.splitext(url)

    return "%s%s%s?%s" % (base_url, action_string, ext, security_hash)


def is_valid_security(action_tuples, security_hash):
    if DEBUG and security_hash == "debug":
        return True
    return create_securityhash(action_tuples) == security_hash


def resolve_request_path(requested_uri):
    """
    Check for any aliases and alter the path accordingly.

    Returns resolved_uri
    """
    for key, val in PATH_ALIASES.items():
        if re.match(key, requested_uri):
            return re.sub(key, val, requested_uri)
    return requested_uri


def parse_action_tuples(filename):
    base_filename, ext = os.path.splitext(filename)

    action_tuples = []
    # split on underscore but keep 'em around in case there are duplicates.
    bits = re.split("(_)", base_filename)
    while bits:
        action = bits.pop()
        if len(action) < 1:
            continue
        if is_valid_actionstring(action):
            action_tuples.insert(0, (action[0], action[1:]))
            bits.pop()  # pop the remaining underscore off the stack
        else:
            bits.append(action)
            break

    base_file_name = "".join(bits)

    return base_file_name, action_tuples


def process_url(url, server_name="", document_root=None):
    """
    Goes through the url and returns a dictionary of fields.

    For example:

    img/photos/2008/05/12/WIZARDS_0034_05022035_r329x151.jpg?e315d4515574cec417b1845392ba687dd98c17ce

    actions:       [('r', '329x151')]
    parent_dir:    img/photos/2008/05/12/
    ext:           jpg
    base_filename: WIZARDS_0034_05022035
    security_hash: e315d4515574cec417b1845392ba687dd98c17ce
    requested_path /path/to/media_root/img/photos/2008/05/12/WIZARDS_0034_05022035_r329x151.jpg
    original_file: /path/to/media_root/img/photos/2008/05/12/WIZARDS_0034_05022035.jpg

    The ``document_root`` parameter overrides the ``BASE_PATH`` setting.
    """
    try:
        request_uri, security_hash = url.split("?", 1)
    except ValueError:
        request_uri, security_hash = url, ""
    resolved_uri = resolve_request_path(request_uri)
    resolved_uri = resolved_uri.lstrip("/")

    base_path = document_root or BASE_PATH
    orig_base_path = ORIG_BASE_PATH or base_path

    if USE_VHOSTS:
        if not os.path.exists(os.path.join(BASE_PATH, server_name)):
            raise Http404("Bad server: %s" % server_name)
        parts = (base_path, server_name, VHOST_DOC_BASE,
                 urllib.unquote(resolved_uri))
        requested_path = os.path.join(*parts)
    else:
        path = os.path.join(base_path, urllib.unquote(resolved_uri))
        requested_path = os.path.abspath(path)
    if not requested_path.startswith(base_path):
        # Apparently, there was an attempt to put some directory traversal
        # hacks into the path. (../../../vulnerable_file.exe)
        raise Http404("Unknown file path.")

    parent_dir, requested_file = os.path.split(resolved_uri)
    base_filename, ext = os.path.splitext(requested_file)

    base_file_name, action_tuples = parse_action_tuples(requested_file)

    if USE_VHOSTS:
        original_file = os.path.join(orig_base_path, server_name, parent_dir, base_file_name + ext)
    else:
        original_file = os.path.join(orig_base_path, parent_dir, base_file_name + ext)

    base_uri = os.path.dirname(resolved_uri)
    original_uri = urlparse.urljoin(base_uri, base_filename + ext)

    if not os.path.exists(original_file):
        msg = "Original file does not exist. %r %r" % (url, original_file, )
        raise Http404(msg)
    if action_tuples and not is_valid_security(action_tuples, security_hash):
        raise Http404("Invalid security token.")
    output = {
        'actions': action_tuples,
        'parent_dir': parent_dir,
        'ext': ext,
        'base_filename': base_filename,
        'security_hash': security_hash,
        'requested_file': requested_path,
        'original_file': original_file,
        'orignial_uri': original_uri,
    }
    return output
