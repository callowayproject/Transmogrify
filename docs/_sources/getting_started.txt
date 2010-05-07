
===============
Getting Started
===============

Transmogrify is a library to dynamically alter images. Its biggest impact is probably how it frees up the designer from resizing images for different designs.

There are several parts to transmogrify. At the core is the image processor. It takes an image file and a set of one or more actions and outputs a new file, predictably renamed, with the actions performed.

.. image:: transmogrify_parts.*

The URL router works with the web server when the processed file doesn't exist. It tells the image processor to create the correct version, allowing the web server to serve the file.

Lastly, the URL generator is a piece of code that generates the URL for the image based on what the designer wants to do with the image.

Currently there is a URL generator for Django (as a template tag), and URL routers for lighttpd (as a 404 handler) and Django (for local serving). Help for other frameworks and servers is greatly appreciated. The image processor is pure python.


The URL Generator
=================

A transmogrify URL consists of action codes and parameters and a SHA1 hash that can prevent others from reusing the images. For example::

/images/funny/clown_rx300_b1-000.jpg?47da31880d05b12f85aedf8b9afc913a6c4e6c12

This URL says take the file at URL ``/images/funny/clown.jpg`` and resize it to 300 pixels high, scaling the width proportionally, then apply a 1 pixel black border. You can verify that it is me (and not some miscreant) with this security hash.

The security hash is a SHA1 hex digest of the actions (``_rx300_b1-000``) and a ``SECRET_KEY``\ . The ``SECRET_KEY`` is set in the ``settings.py`` file.

Django Template Tag
*******************

For Django, there is a template tag to generate the correct URL.