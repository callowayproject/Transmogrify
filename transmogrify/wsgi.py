#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
import urlparse
from hashlib import sha1
from settings import DEBUG
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


def app(environ, start_response):
    cropname = None
    server = environ['SERVER_NAME']
    quality = 80

    request_uri = environ.get('REQUEST_URI', environ.get('RAW_URI', ''))
    path_and_query = request_uri.lstrip("/")
    if path_and_query is "":
        return do404(environ, start_response, "Not Found", DEBUG)

    # Acquire lockfile
    lock = '/tmp/%s' % sha1(path_and_query).hexdigest()
    if os.path.isfile(lock):
        return doRedirect(environ, start_response, request_uri)

    with lock_file(lock):
        try:
            url_parts = process_url(path_and_query, server)
            output_path, _ = os.path.split(url_parts['requested_file'])
            makedirs(output_path)
        except Http404, e:
            return do404(environ, start_response, e.message, DEBUG)

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


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    s = make_server("", 3031, app())
    print "Serving on port 3031"
    s.serve_forever()
