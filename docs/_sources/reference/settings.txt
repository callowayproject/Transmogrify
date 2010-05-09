.. _settings:

========
Settings
========


.. _transmogrify_secret:

``TRANSMOGRIFY_SECRET``
=======================

This is any string that is shared between the various servers involved. It is used to create the SHA1 hash. The SHA1 hash is simply used to prevent external sites from requesting arbitrary image alterations.

**Default:** ``""``

.. _transmogrify_debug:

``TRANSMOGRIFY_DEBUG``
======================

This turns on debug mode, which returns more descriptive error messages and stack traces.

**Default:** ``False``

.. _transmogrify_base_path:

``TRANSMOGRIFY_BASE_PATH``
==========================

This is the root from where the images are located. If ``TRANSMOGRIFY_BASE_PATH`` is ``/home/media/``\ , a request for file ``/images/spanish_inquisition.png`` is looked for at ``/home/media/images/spanish_inquisition.png``\ . The request's path can be altered with :ref:`transmogrify_path_aliases`\ .

**Default:** ``/home/media/``

.. _transmogrify_path_aliases:

``TRANSMOGRIFY_PATH_ALIASES``
=============================

Typically the location of the original file to modify is derived from::

	TRANSMOGRIFY_BASE_PATH + requested_url

Sometimes this isn't very useful, as the actual paths of the files don't make for good URLs. ``TRANSMOGRIFY_PATH_ALIASES`` allows you to set regular expressions to alter incoming URLs.

``TRANSMOGRIFY_PATH_ALIASES`` is a dictionary of ``{'<url_regex>': '<sub_regex>'}``\ . Each request is matched against the keys. The first match is substituted using that key's value. For example if your images were stored in ``/home/www/assets/images/``\ , but the URL was ``/media/images/``\ , you would set::

	TRANSMOGRIFY_BASE_PATH = "/home/www"
	TRANSMOGRIFY_PATH_ALIASES = {'/media/':'/assets/'}

so requests for ``/media/images/sample.jpg`` converts into ``/assets/images/sample.jpg`` and when added to ``/home/www`` you get the file.

**Default:** ``{}``


.. _transmogrify_use_vhosts:

``TRANSMOGRIFY_USE_VHOSTS``
===========================

Allows for the use of simple lighttpd vhosts. This hasn't been fully tested yet.

**Default:** ``False``

.. _transmogrify_vhost_doc_base:

``TRANSMOGRIFY_VHOST_DOC_BASE``
===============================

Used with :ref:`transmogrify_use_vhosts` to locate the original document.

**Default:** ``""``

.. _transmogrify_no_img_url:

``TRANSMOGRIFY_NO_IMG_URL``
===========================

Allows for a generic image to return if the original file isn't found.

**Default:** ``""``
