#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
import urlparse
from hashlib import sha1
from utils import process_url, Http404
from transmogrify import Transmogrify
from contextlib import contextmanager


@contextmanager
def lock_file(lock):
    open(lock, "w")

    try:
        yield
    finally:
        # Remove lockfile
        os.remove(lock)


def makedirs(dirname):
    assert dirname.startswith("/"), "dirname must be absolute"

    bits = dirname.split(os.sep)[1:]

    root = "/"

    for bit in bits:
        root = os.path.join(root, bit)

        if not os.path.lexists(root):
            os.mkdir(root)
        elif not os.path.isdir(root):
            raise OSError("%s is exists, but is not a directory." % (root, ))
        else:  # exists and is a dir
            pass


def get_path(environ):
    """
    Get the path
    """
    from wsgiref import util
    request_uri = environ.get('REQUEST_URI', environ.get('RAW_URI', ''))
    if request_uri == '':
        uri = util.request_uri(environ)
        host = environ.get('HTTP_HOST', '')
        scheme = util.guess_scheme(environ)
        prefix = "{scheme}://{host}".format(scheme=scheme, host=host)
        request_uri = uri.replace(prefix, '')
    return request_uri


def handle_purge(environ, start_response):
    """
    Handle a PURGE request.
    """
    from utils import is_valid_security, get_cached_files
    from settings import DEBUG
    server = environ['SERVER_NAME']
    try:
        request_uri = get_path(environ)
        path_and_query = request_uri.lstrip("/")
        query_string = environ.get('QUERY_STRING', '')
        if is_valid_security('PURGE', query_string):
            cached_files = get_cached_files(path_and_query, server)
            for i in cached_files:
                try:
                    os.remove(i)
                except OSError as e:
                    return do_500(environ, start_response, e.message)
            start_response("204 No Content", [])
            return []
        else:
            return do_405(environ, start_response)
    except Http404 as e:
        return do_404(environ, start_response, e.message, DEBUG)


def app(environ, start_response):
    from settings import DEBUG

    cropname = None
    server = environ['SERVER_NAME']
    quality = 80

    request_uri = get_path(environ)
    path_and_query = request_uri.lstrip('/')
    if path_and_query is "":
        return do_404(environ, start_response, "Not Found", DEBUG)

    if environ.get('REQUEST_METHOD', 'GET') == 'PURGE':
        return handle_purge(environ, start_response)

    # Acquire lockfile
    lock = '/tmp/%s' % sha1(path_and_query).hexdigest()
    if os.path.isfile(lock):
        return do_redirect(environ, start_response, request_uri)

    with lock_file(lock):
        try:
            url_parts = process_url(path_and_query, server)
            output_path, _ = os.path.split(url_parts['requested_file'])
            makedirs(output_path)
            if not os.path.exists(url_parts['original_file']):
                raise Http404
            if not os.path.isfile(url_parts['original_file']):
                raise Http404
        except Http404 as e:
            return do_404(environ, start_response, e.message, DEBUG)

        new_file = Transmogrify(
            url_parts['original_file'],
            url_parts['actions'],
            quality=quality,
            output_path=output_path
        )
        new_file.cropname = cropname
        new_file.save()

        if cropname:
            # Rewrite the request_uri to use the new file with the
            # cropname
            urlbits = list(urlparse.urlsplit(request_uri))
            output_filename = new_file.get_processed_filename()
            filename = os.path.basename(output_filename)
            requested_dir = os.path.dirname(urlbits[2])
            urlbits[2] = os.path.join(requested_dir, filename)
            request_uri = urlparse.urlunsplit(urlbits)

        return do_redirect(environ, start_response, request_uri)


def do_redirect(environ, start_response, path):
    # if get_path(environ) == path:
    #     return do_500(environ, start_response, 'Redirect Loop Detected')
    start_response("302 Found", [("Location", path)])
    return []


def do_500(environ, start_response, message):
    resp = {
        'message': message,
        'status_code': 500,
        'status_message': 'Internal Server Error',
    }

    start_response("500 Internal Server Error", [("Content-Type", "text/html")])
    return [ERROR.format(**resp)]


def do_405(environ, start_response):
    resp = {
        'message': "Method not allowed",
        'status_code': 405,
        'status_message': 'Method Not Allowed',
    }

    start_response("405 Method Not Allowed", [("Content-Type", "text/html")])
    return [ERROR.format(**resp)]


def do_404(environ, start_response, why, debug):
    if debug:
        message = "<h2>%s</h2>" % why
    else:
        message = "File not found"
    resp = {
        'message': message,
        'status_code': 404,
        'status_message': 'Not Found',
    }

    start_response("404 Not Found", [("Content-Type", "text/html")])
    return [ERROR.format(**resp)]


ERROR = """
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
 <head>
  <title>{status_code} - {status_message}</title>
 </head>
 <body>
  <h1>{status_code} - {status_message}</h1>{message}
 </body>
</html>
"""


class DemoApp(object):
    def __init__(self):
        from static import Cling
        from settings import BASE_PATH

        self.app = Cling(BASE_PATH)
        self.fallback = app

    def __call__(self, environ, start_response):
        import wsgiref
        response = {}

        def sr(status, headers):
            response['status'] = status
            response['headers'] = headers

        result = self.app(environ, sr)

        if response['status'] == '404 Not Found':
            request_uri = wsgiref.util.request_uri(environ)
            p = urlparse.urlparse(request_uri)
            if p.query:
                request_uri = p.path + "?" + p.query
            else:
                request_uri = p.path

            environ['REQUEST_URI'] = request_uri
            return self.fallback(environ, start_response)
        elif response['status'] == '405 Method Not Allowed':
            request_uri = wsgiref.util.request_uri(environ)
            p = urlparse.urlparse(request_uri)
            if p.query:
                request_uri = p.path + "?" + p.query
            else:
                request_uri = p.path

            environ['REQUEST_URI'] = request_uri
            return self.fallback(environ, start_response)
        else:
            start_response(response['status'], response['headers'])
            return result


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    from utils import create_securityhash, create_purge_securityhash
    s = make_server("", 3031, DemoApp())
    print "Serving on port 3031"
    security_hash = create_securityhash([('c', '0-410-300-710')])
    purge_hash = create_purge_securityhash()
    print "try http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % security_hash
    print "try purging http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % purge_hash
    print create_securityhash([('r', '200x22')])
    s.serve_forever()
