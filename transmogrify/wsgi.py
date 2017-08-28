#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
from hashlib import sha1
from contextlib import contextmanager
from .core import Transmogrify
from .network import Http404, do_404, handle_purge, do_redirect, get_path


@contextmanager
def lock_file(lock):
    open(lock, "w")

    try:
        yield
    finally:
        # Remove lockfile
        os.remove(lock)


def app(environ, start_response):
    from settings import DEBUG

    request_uri = get_path(environ)
    path_and_query = request_uri.lstrip('/')
    if path_and_query is "":
        return do_404(environ, start_response, "Not Found", DEBUG)

    if environ.get('REQUEST_METHOD', 'GET') == 'PURGE':
        return handle_purge(environ, start_response)

    # Acquire lockfile
    lock = '/tmp/%s' % sha1(path_and_query).hexdigest()
    if os.path.isfile(lock):
        return do_404(environ, start_response, "File is being processed", DEBUG)

    with lock_file(lock):
        try:
            server = environ['SERVER_NAME']
            new_file = Transmogrify(path_and_query, server)
            new_file.save()
        except Http404 as e:
            return do_404(environ, start_response, e.message, DEBUG)

        return do_redirect(environ, start_response, request_uri)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    from utils import create_securityhash, create_purge_securityhash
    from .network import DemoApp
    s = make_server("", 3031, DemoApp(fallback=app))
    print "Serving on port 3031"
    security_hash = create_securityhash([('c', '0-410-300-710')])
    purge_hash = create_purge_securityhash()
    print "try http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % security_hash
    print "try purging http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % purge_hash
    print create_securityhash([('r', '200x22')])
    s.serve_forever()
