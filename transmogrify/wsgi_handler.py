#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
import sys
import re
from settings import DEBUG, FALLBACK_SERVERS, BASE_PATH
from utils import process_url, Http404, parse_action_tuples
from transmogrify import Transmogrify
from hashcompat import sha_constructor
from contextlib import contextmanager
import time
from pprint import pformat, pprint
import urllib, urlparse, shutil
import wsgiref.util

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
        

def match_fallback(fallback_servers, path_info):
    print "Matching..."
    for pattern, replace, server in fallback_servers:
        if re.match(pattern, path_info):

            new_path = re.sub(pattern, replace, path_info)
            print "Matched %r %r %r %r" % (pattern, replace, path_info, (new_path, server))
            return (new_path, server)


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
            print "downloaded %s to %s" % (fallback_url, output_file)
            return (True, tmpfn)
        except IOError, e:
            return (False, (e, (fallback_url, output_file)))
    else:
        return (False, ("file exists", output_file))


def app(environ, start_response):
    server = environ['SERVER_NAME']
    request_uri = environ['REQUEST_URI']
    path_and_query = request_uri.lstrip("/")
    requested_path = urlparse.urlparse(path_and_query).path
    
    # Acquire lockfile
    lock = '/tmp/%s' % sha_constructor(path_and_query).hexdigest()

    if os.path.isfile(lock):
        return doRedirect(environ, start_response, request_uri)

    with lock_file(lock):

        if FALLBACK_SERVERS:
            result = do_fallback(FALLBACK_SERVERS, BASE_PATH, requested_path)
            print "fallback: %r" % (result, )
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
    print "Redirecting to %r" % (path, )
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
