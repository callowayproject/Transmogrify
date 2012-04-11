#!/bin/env python

"""
Apache 404 handler for mogrifying images.
"""

import os
import sys
from settings import DEBUG
from utils import process_url, Http404
from transmogrify import Transmogrify
from hashcompat import sha_constructor
from contextlib import contextmanager
import time
from pprint import pformat


@contextmanager
def lock_file(lock):
    open(lock, "w")

    try:
        yield
    finally:
        # Remove lockfile
        os.remove(lock)
    

def app(environ, start_response):
    server = environ['SERVER_NAME']
    path   = environ['REQUEST_URI']
    

    # Acquire lockfile
    lock = '/tmp/%s' % sha_constructor(path).hexdigest()

    if os.path.isfile(lock):
        return doRedirect(environ, start_response, path)

    

    with lock_file(lock):
        try:
            url_parts = process_url(path, server)
        except Http404, e:
            return do404(environ, start_response, e.message, DEBUG)


        new_file = Transmogrify(url_parts['original_file'], url_parts['actions'])
        new_file.save()

        return doRedirect(environ, start_response, path)


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

