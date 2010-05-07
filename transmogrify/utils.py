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
import os, re, urllib
from settings import BASE_PATH, USE_VHOSTS, VHOST_DOC_BASE, PROCESSORS, SECRET_KEY
from hashcompat import sha_constructor

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
    security_hash = sha_constructor(action_string + SECRET_KEY).hexdigest()
    return security_hash

def is_valid_security(action_tuples, security_hash):
    return create_securityhash(action_tuples) == security_hash

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
    request_uri = request_uri.lstrip("/")
    
    base_path = document_root or BASE_PATH
    
    if USE_VHOSTS:
        if not os.path.exists(os.path.join(BASE_PATH, server)):
            raise Http404("Bad server: %s" % server)
        requested_path = os.path.join(base_path, server, VHOST_DOC_BASE, urllib.unquote(request_uri))
    else:
        requested_path = os.path.abspath(os.path.join(base_path, urllib.unquote(request_uri)))
    if not requested_path.startswith(base_path):
        # Apparently, there was an attempt to put some directory traversal
        # hacks into the path. (../../../vulnerable_file.exe)
        raise Http404("Unknown file path.")
    
    parent_dir, requested_file = os.path.split(requested_path)
    base_filename, ext = os.path.splitext(requested_file)
    
    action_tuples = []
    # split on underscore but keep 'em around in case there are duplicates.
    bits = re.split("(_)", base_filename)
    while bits:
        action = bits.pop()
        if len(action) < 1:
            continue
        if is_valid_actionstring(action):
            action_tuples.insert(0, (action[0], action[1:]))
            bits.pop() # pop the remaining underscore off the stack
        else:
            bits.append(action)
            break
    
    base_file_name = "".join(bits)
    original_file = os.path.join(parent_dir, base_file_name + ext)
    if not os.path.exists(original_file):
        raise Http404("Original file does not exist.")
    if not is_valid_security(action_tuples, security_hash):
        raise Http404("Invalid security token.")
    return {
        'actions': action_tuples,
        'parent_dir': parent_dir,
        'ext': ext,
        'base_filename': base_filename,
        'security_hash': security_hash,
        'requested_file': requested_path,
        'original_file': original_file
    }
    