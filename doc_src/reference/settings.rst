.. _settings:

========
Settings
========

Transmogrify's settings can be specified via a settings file, or via environment variables, or both. The ``TRANSMOGRIFY_SETTINGS`` environment variable specifies the python file to import. You may also specify one or more settings as environment variables by prefixing ``TRANSMOGRIFY_`` to the name of the setting, such as ``TRANSMOGRIFY_SECRET_KEY``\ .

.. _transmogrify_base_path:

``BASE_PATH``
=============

**Default:** ``/home/media/``

This is the root from where the modified images are located. If ``BASE_PATH`` is ``/home/media/``\ , a request for file ``/images/spanish_inquisition.png`` is looked for at ``/home/media/images/spanish_inquisition.png``\ . The request's path can be altered with :ref:`transmogrify_path_aliases`\ .



.. _transmogrify_debug:

``DEBUG``
=========

**Default:** ``False``

This turns on debug mode, which returns more descriptive error messages and stack traces.


.. _external_prefix:

``EXTERNAL_PREFIX``
===================

**Default:** ``"/external/"``

Image requests prefixed with this path are considered external images that must be fetched from the URL-encoded path before any modifications are made.

Any false-y value (e.g. empty string, ``False``, or ``None``) turns this off.


.. _fallback_servers:

``FALLBACK_SERVERS``
====================

**Default:** ``()``

TBD


.. _transmogrify_image_optimization_cmd:

``IMAGE_OPTIMIZATION_CMD``
==========================

**Default:** ``""``

A  `python template string`_ including the command and options to optimize images. It must include "``{filename}``" for substitution of the file path to optimize.

Any false-y value (e.g. empty string, ``False``, or ``None``) turns this off.

Example::

    "IMAGE_OPTIMIZATION_CMD": "/usr/bin/picopt -GQaYM {filename}"


.. _python template string: https://docs.python.org/2/library/string.html#format-string-syntax


.. _transmogrify_no_img_url:

``NO_IMG_URL``
==============

**Default:** ``""``

Allows for a generic image to return if the original file isn't found.


.. _transmogrify_opencv_prefix:

``OPENCV_PREFIX``
=================

**Default:** ``"/usr/local/share/"``

OpenCV is used for automatic face detection, if requested for automatic cropping.


.. _transmogrify_orig_base_path

``ORIG_BASE_PATH``
==================

**Default:** ``"/home/media/"``

This is where the original images are stored.


.. _transmogrify_path_aliases:

``PATH_ALIASES``
================

**Default:** ``{}``


.. _transmogrify_secret:

``SECRET_KEY``
==============

**Default:** ``""``

This is any string that is shared between the various servers involved. It is used to create the SHA1 hash. The SHA1 hash is simply used to prevent external sites from requesting arbitrary image alterations.


.. _transmogrify_use_vhosts:

``USE_VHOSTS``
===========================

Allows for the use of simple lighttpd vhosts. This hasn't been fully tested yet.

**Default:** ``False``

.. _transmogrify_vhost_doc_base:

``VHOST_DOC_BASE``
===============================

Used with :ref:`transmogrify_use_vhosts` to locate the original document.

**Default:** ``""``

