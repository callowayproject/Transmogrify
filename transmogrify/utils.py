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


class Http404(Exception):
    pass


def download_url(url, destination):
    """
    Download an external URL to the destination
    """
    import os
    import urllib
    from settings import VALID_IMAGE_EXTENSIONS
    base_name, ext = os.path.splitext(url)
    ext = ext.lstrip('.')

    if ext not in VALID_IMAGE_EXTENSIONS:
        raise Exception("Invalid image extension")

    base_path, filename = os.path.split(destination)
    os.makedirs(base_path)
    urllib.urlretrieve(url, destination)


def is_valid_actionstring(action_string):
    from settings import PROCESSORS
    code, arg = action_string[0], action_string[1:]

    return code in PROCESSORS and PROCESSORS[code].param_pattern().match(arg)


def create_securityhash(action_tuples):
    """
    Create a SHA1 hash based on the KEY and action string
    """
    from settings import SECRET_KEY

    action_string = "".join(["_%s%s" % a for a in action_tuples])
    security_hash = sha1(action_string + SECRET_KEY).hexdigest()
    return security_hash


def create_purge_securityhash():
    """
    Create a SHA1 hsh based on the KEY and 'PURGE'
    """
    from settings import SECRET_KEY
    security_hash = sha1('PURGE' + SECRET_KEY).hexdigest()
    return security_hash


def generate_url(url, action_string):
    from settings import SECRET_KEY

    security_hash = sha1(action_string + SECRET_KEY).hexdigest()
    base_url, ext = os.path.splitext(url)

    return "%s%s%s?%s" % (base_url, action_string, ext, security_hash)


def is_valid_security(action_tuples, security_hash):
    from settings import DEBUG

    if DEBUG and security_hash == "debug":
        return True
    if action_tuples == 'PURGE':
        return create_purge_securityhash() == security_hash
    else:
        return create_securityhash(action_tuples) == security_hash


def resolve_request_path(requested_uri):
    """
    Check for any aliases and alter the path accordingly.

    Returns resolved_uri
    """
    from settings import PATH_ALIASES

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
            if bits and bits[-1] == '_':
                bits.pop()  # pop the remaining underscore off the stack
        else:
            bits.append(action)
            break

    base_file_name = "".join(bits)

    return base_file_name, action_tuples


def process_url(url, server_name="", document_root=None, check_security=True):
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
    is_external:   False

    The ``document_root`` parameter overrides the ``BASE_PATH`` setting.
    """
    from settings import (BASE_PATH, ORIG_BASE_PATH, USE_VHOSTS, VHOST_DOC_BASE, EXTERNAL_PREFIX)

    try:
        request_uri, security_hash = url.split("?", 1)
    except ValueError:
        request_uri, security_hash = url, ""

    external_prefix = EXTERNAL_PREFIX.lstrip("/")
    is_external = request_uri.startswith(external_prefix)
    resolved_uri = resolve_request_path(request_uri)
    resolved_uri = resolved_uri.lstrip("/")
    resolved_uri = urllib.unquote(resolved_uri)
    if is_external:
        external_url = urllib.unquote(resolved_uri.replace(external_prefix, ''))
        resolved_uri = resolved_uri.replace("http://", '').replace('https://', '')
    else:
        external_url = ''

    base_path = document_root or BASE_PATH
    orig_base_path = ORIG_BASE_PATH or base_path

    if USE_VHOSTS:
        if not os.path.exists(os.path.join(BASE_PATH, server_name)):
            raise Http404("Bad server: %s" % server_name)
        parts = (base_path, server_name, VHOST_DOC_BASE,
                 resolved_uri)
        requested_path = os.path.join(*parts)
    else:
        path = os.path.join(base_path, resolved_uri)
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
    original_is_missing = not os.path.exists(original_file)

    if original_is_missing and is_external:
        try:
            download_url(external_url, original_file)
        except Exception as e:
            msg = "Error downloading external URL: %s" % e
            raise Http404(msg)
    elif original_is_missing:
        msg = "Original file does not exist. %r %r" % (url, original_file, )
        raise Http404(msg)
    if check_security and action_tuples and not is_valid_security(action_tuples, security_hash):
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
        'is_external': is_external,
        'external_url': external_url,
    }
    return output


def get_cached_files(url, server_name="", document_root=None):
    """
    Given a URL, return a list of paths of all cached variations of that file.

    Doesn't include the original file.
    """
    import glob
    url_info = process_url(url, server_name, document_root, check_security=False)

    # get path to cache directory with basename of file (no extension)
    filedir = os.path.dirname(url_info['requested_file'])
    fileglob = '{0}*{1}'.format(url_info['base_filename'], url_info['ext'])
    return glob.glob(os.path.join(filedir, fileglob))
