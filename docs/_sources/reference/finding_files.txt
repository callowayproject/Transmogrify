.. _finding_files:

===========================
Locating and storing images
===========================

Original files
==============

You store your original files in either ``ORIG_BASE_PATH`` or ``ORIG_BASE_PATH/VIRTUAL_HOST/``

How local images are located and stored
=======================================

The basic structure of the file path is::

    ORIG_BASE_PATH + REQUESTED_PATH

or if using virtual hosts::

    ORIG_BASE_PATH + VIRTUAL_HOST + REQUESTED_PATH

How external images are located and stored
==========================================

The basic structure of the file path is::

    ORIG_BASE_PATH + EXTERNAL_PREFIX + EXTERNAL_URL

or if using virtual hosts::

    ORIG_BASE_PATH + VIRTUAL_HOST + EXTERNAL_PREFIX + EXTERNAL_URL

In the case of external images, the file's entire URL becomes its name, because the file's entire URL is URL-encoded into the request. This allows the HTTP server front end to look for the file easily.


Modifying the requested file path
=================================

The setting :ref:`transmogrify_path_aliases` allows you to set regular expressions to alter incoming URLs.

``PATH_ALIASES`` is a dictionary of ``{'<url_regex>': '<sub_regex>'}``\ . Each request is matched against the keys. The first match is substituted using that key's value. For example if your images were stored in ``/home/www/assets/images/``\ , but the URL was ``/media/images/``\ , you would set::

    ORIG_BASE_PATH = "/home/www"
    PATH_ALIASES = {'/media/':'/assets/'}

so requests for ``/media/images/sample.jpg`` converts into ``/assets/images/sample.jpg`` and when added to ``/home/www`` you get the file.
