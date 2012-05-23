#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
import sys
from settings import DEBUG, FALLBACK_SERVER, BASE_PATH
from utils import process_url, Http404, parse_action_tuples
from transmogrify import Transmogrify
from hashcompat import sha_constructor
from contextlib import contextmanager
import time
from pprint import pformat
import urllib, urlparse, shutil
import wsgiref.util

print "fallback server ", FALLBACK_SERVER

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
        else: # exists and is a dir
            pass
        

def do_fallback(fallback_server, base_path, path_info):
    _, ext = os.path.splitext(path_info)
    path_info = path_info.lstrip("/")
    path_info, action_tuples = parse_action_tuples(path_info)
    path_info = path_info + ext

    if ".." in path_info:
        return (False, "bad path")
    else:
        output_file = os.path.join(base_path, path_info)

        fallback_url = urlparse.urljoin(fallback_server, path_info)

        if not os.path.lexists(output_file):
            o = urllib.URLopener()
            try:
                (tmpfn, httpmsg) = o.retrieve(fallback_url)

                makedirs(os.path.dirname(output_file))
                shutil.move(tmpfn, output_file)
                print "downloaded %s to %s" % (fallback_url, output_file)
                return (True, tmpfn)
            except IOError, e:
                return (False, e)
        


def app(environ, start_response):
    server = environ['SERVER_NAME']
    path_info   = environ['PATH_INFO']
    query  = environ.get("QUERY_STRING", "")
    if query:
        path_and_query = path_info + "?" + query
    else:
        path_and_query = path_info

    request_uri = path_and_query

    # Acquire lockfile
    lock = '/tmp/%s' % sha_constructor(path_and_query).hexdigest()

    if os.path.isfile(lock):
        return doRedirect(environ, start_response, request_uri)

    with lock_file(lock):

        if FALLBACK_SERVER and path_info:
            result = do_fallback(FALLBACK_SERVER, BASE_PATH, path_info)
            if result == (False, "bad path"):
                start_response("403 Forbidden", [])
                return []

        try:
            url_parts = process_url(path_and_query, server)
        except Http404, e:
            return do404(environ, start_response, e.message, DEBUG)

        new_file = Transmogrify(url_parts['original_file'], url_parts['actions'])
        new_file.save()

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
    s = make_server("", 8000, app)
    print "Serving on port 8000"
    s.serve_forever()
