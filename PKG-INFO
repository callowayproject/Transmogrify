============
Transmogrify
============

Transmogrify is a Python-based image manipulator. It allows for dynamic alteration of images using the URL of the image. The biggest benefit is to the web designer, as images can be scaled to fit the design on the fly.

Transmogrify is a library to dynamically alter images. Its biggest impact is probably how it frees up the designer from resizing images for different designs.

Three parts to Transmogrify
===========================

::

	+----------------------+        +----------------------+
	|      Web Server      |        |     Media Server     |
	|                      |        |                      |
	|    URL Generator     |        |      URL Router      |
	|                      |        |   Image Processor    |
	+----------------------+        +----------------------+


There are several parts to transmogrify. At the core is the image processor. It takes an image file and a set of one or more actions and outputs a new file, predictably renamed, with the actions performed. The media server can now serve this image as normal.

The URL router works with the web server when the processed file doesn't exist. It tells the image processor to create the correct version, allowing the web server to serve the file.

Lastly, the URL generator is a piece of code that generates the URL for the image based on what the designer wants to do with the image.


Implementations
===============

Currently there is a URL generator for Django (as a template tag), and URL routers for lighttpd (as a 404 handler) and Django (for local serving). 

Help for other frameworks and servers is greatly appreciated. The image processor is pure python and is based on PIL.

