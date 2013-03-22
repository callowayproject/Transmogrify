#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
import re
import urllib
import urlparse
import shutil
import wsgiref.util
from settings import DEBUG, FALLBACK_SERVERS, BASE_PATH
from utils import process_url, Http404, parse_action_tuples
from transmogrify import Transmogrify
from hashlib import sha1
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


def match_fallback(fallback_servers, path_info):
    for pattern, replace, server in fallback_servers:
        if re.match(pattern, path_info):

            new_path = re.sub(pattern, replace, path_info)
            new_server = re.sub(pattern, server, path_info)
            return urlparse.urljoin(new_server, new_path)


def do_fallback(fallback_servers, base_path, path_info):
    _, ext = os.path.splitext(path_info)
    path_info = path_info.lstrip("/")
    path_info, action_tuples = parse_action_tuples(path_info)
    path_info = path_info + ext

    if ".." in path_info:
        return (False, "bad path")

    match = match_fallback(fallback_servers, path_info)

    if not match:
        return (False, "no matching fallback")

    remote_path, fallback_server = match
    fallback_url = urlparse.urljoin(fallback_server, remote_path)
    output_file = os.path.join(base_path, path_info)

    if not os.path.lexists(output_file):
        o = urllib.URLopener()
        try:
            (tmpfn, httpmsg) = o.retrieve(fallback_url)

            makedirs(os.path.dirname(output_file))
            shutil.move(tmpfn, output_file)
            return (True, tmpfn)
        except IOError, e:
            return (False, (e, (fallback_url, output_file)))
    else:
        return (False, ("file exists", output_file))


def app(environ, start_response):
    cropname = None
    server = environ['SERVER_NAME']
    quality = 80

    if "path=" in environ.get("QUERY_STRING", ""):
        # I should probably require a POST for this, but meh, let's not
        # rock the boat.

        # transmogrify is being used directly and not as a 404 handler
        query_dict = urlparse.parse_qs(environ['QUERY_STRING'])

        path = query_dict.get("path", [""])[0]
        key = query_dict.get("key", [""])[0]

        # validate the query params
        if not (path and key):
            # The required parameters were not given
            start_response("400 Bad Response",
                           [("Content-Type", "text/plain")])
            return ["path and key are required query parameters"]

        cropname = query_dict.get("cropname", [None])[0]
        quality = 100

        # rewrite the environ to look like a 404 handler
        environ['REQUEST_URI'] = path + "?" + key

    request_uri = environ['REQUEST_URI']
    path_and_query = request_uri.lstrip("/")
    requested_path = urlparse.urlparse(path_and_query).path

    if path_and_query is "":
        return do404(environ, start_response, "Not Found", DEBUG)

    # Acquire lockfile
    lock = '/tmp/%s' % sha1(path_and_query).hexdigest()

    if os.path.isfile(lock):
        return doRedirect(environ, start_response, request_uri)

    with lock_file(lock):

        if FALLBACK_SERVERS:
            result = do_fallback(FALLBACK_SERVERS, BASE_PATH, requested_path)
            if result == (False, "bad path"):
                start_response("403 Forbidden", [])
                return []

        try:
            url_parts = process_url(path_and_query, server)
        except Http404, e:
            return do404(environ, start_response, e.message, DEBUG)

        new_file = Transmogrify(
            url_parts['original_file'],
            url_parts['actions'],
            quality=quality
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

        return doRedirect(environ, start_response, request_uri)


def doRedirect(environ, start_response, path):
    start_response("302 Found", [("Location", path)])
    return []


def do404(environ, start_response, why, debug):

    if debug:
        message = "<h2>%s</h2>" % why
    else:
        message = "File not found"

    start_response("404 Not Found", [("Content-Type", "text/html")])
    return [ERROR_404 % message]


ERROR_404 = """
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
 <head>
  <title>404 - Not Found</title>
 </head>
 <body>
  <h1>404 - Not Found</h1>%s
 </body>
</html>
"""

class DemoApp(object):
    def __init__(self):
        from static import Cling
        self.app = Cling(BASE_PATH)
        self.fallback = app

    def __call__(self, environ, start_response):
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
        else:
            start_response(response['status'], response['headers'])
            return result


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    s = make_server("", 8000, DemoApp())
    print "Serving on port 8000"
    s.serve_forever()
