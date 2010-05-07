import re, os

from django.views.static import serve
from django.http import Http404

import utils
from transmogrify import Transmogrify

HEXDIGEST_RE = re.compile(r"^[a-f0-9]{40}$")

def transmogrify_serve(request, path, document_root=None, show_indexes=False):
    if HEXDIGEST_RE.match(request.META['QUERY_STRING']):
        try:
            request_uri = "%s?%s" % (path, request.META['QUERY_STRING'])
            server = request.META["SERVER_NAME"].split(":")[0]
            url_parts = utils.process_url(request_uri, server, document_root)
            if not os.path.exists(url_parts['requested_file']):
                new_file = Transmogrify(url_parts['original_file'], url_parts['actions'])
                new_file.save()
        except utils.Http404, e:
            raise Http404(e)
    return serve(request, path, document_root, show_indexes)

