#!/bin/env python

"""
WSGI handler for mogrifying images.
"""

import os
from hashlib import sha1
from utils import process_url
from transmogrify import Transmogrify
from contextlib import contextmanager
from .network import Http404, do_404, handle_purge, do_redirect, get_path


@contextmanager
def lock_file(lock):
    open(lock, "w")

    try:
        yield
    finally:
        # Remove lockfile
        os.remove(lock)


def makedirs(dirname):
    if dirname.startswith("s3://"):
        # S3 will make the directories when we submit the file
        return
    else:
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


def validate_original_file(original_file):
    """
    Check to make sure the original file exists
    """
    if original_file.startswith("s3://"):
        import s3
        s3.validate_original_file(original_file)
    else:
        if not os.path.exists(original_file):
            raise Http404
        if not os.path.isfile(original_file):
            raise Http404


def app(environ, start_response):
    from settings import DEBUG

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
        return do_404(environ, start_response, "File is being processed", DEBUG)

    with lock_file(lock):
        try:
            url_parts = process_url(path_and_query, server)
            output_path, _ = os.path.split(url_parts['requested_file'])
            makedirs(output_path)
            validate_original_file(url_parts['original_file'])
        except Http404 as e:
            return do_404(environ, start_response, e.message, DEBUG)

        new_file = Transmogrify(
            url_parts['original_file'],
            url_parts['actions'],
            quality=quality,
            output_path=output_path
        )
        new_file.save()

        return do_redirect(environ, start_response, request_uri)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    from utils import create_securityhash, create_purge_securityhash
    from .network import DemoApp
    s = make_server("", 3031, DemoApp())
    print "Serving on port 3031"
    security_hash = create_securityhash([('c', '0-410-300-710')])
    purge_hash = create_purge_securityhash()
    print "try http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % security_hash
    print "try purging http://localhost:3031/horiz_img_c0-410-300-710.jpg?%s" % purge_hash
    print create_securityhash([('r', '200x22')])
    s.serve_forever()
