#!/bin/env python

"""
Apache 404 handler for mogrifying images.
"""

import os
from settings import DEBUG
from utils import process_url, Http404
from transmogrify import Transmogrify
from hashcompat import sha_constructor
from contextlib import contextmanager
import time


@contextmanager
def lock_file(lock):
    open(lock, "w")

    try:
        yield
    finally:
        # Remove lockfile
        os.remove(lock)


def handle_request():
    server = os.environ["SERVER_NAME"].split(":")[0]
    path = os.environ["REQUEST_URI"]

    # Acquire lockfile
    lock = '/tmp/%s' % sha_constructor(path).hexdigest()
    if os.path.isfile(lock):
        doRedirect(path)
        return

    with lock_file(lock):
        if DEBUG:
            import cgitb
            cgitb.enable()

        try:
            url_parts = process_url(path, server)
        except Http404, e:
            do404(e.message, DEBUG)
            return

        new_file = Transmogrify(url_parts['original_file'], url_parts['actions'])
        new_file.save()

        doRedirect(path)


def doRedirect(path):
    time.sleep(0.005)
    print "Status: 302 Found"
    print "Location: %s" % path
    print


def do404(why, debug):
    if debug:
        message = "<h2>%s</h2>" % why
    else:
        message = "File not found"
    print "Status: 404"
    print "Content-type: text/html"
    print
    print ERROR_404 % message

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
    handle_request()
