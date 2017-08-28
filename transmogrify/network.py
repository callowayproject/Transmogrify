import os
import urlparse


class Http404(Exception):
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
    def __init__(self, fallback):
        from static import Cling
        from settings import BASE_PATH

        self.app = Cling(BASE_PATH)
        self.fallback = fallback

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
