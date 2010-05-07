"""
lighttpd 404 handler for mogrifying images.
"""

import os
import sys
from settings import DEBUG
from utils import process_url, Http404
from transmogrify import Transmogrify

def handle_request():
    if DEBUG:
        import cgitb
        cgitb.enable()
    
    try:
        server = os.environ["SERVER_NAME"].split(":")[0]
        url_parts = process_url(os.environ['REQUEST_URI'], server)
    except Http404, e:
        do404(e.message, DEBUG)
    
    new_file = Transmogrify(url_parts['original_file'], url_parts['actions'])
    new_file.save()
    
    print "Location: /%s" % os.environ['REQUEST_URI']
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
    sys.exit(0)

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