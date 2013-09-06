============
Installation
============


Install optional Pillow requirements
====================================

Pillow requires certain native libraries in order to decode certain types of files.

Typically you will need these libraries (these are the Ubuntu names):

* libjpeg
* libjpeg-dev
* libfreetype6
* libfreetype6-dev
* zlib1g-dev

If you want Transmogrify to also better handle the conversion of CMYK images to RGB, you need to add littleCMS_ libaries.

* liblcms
* liblcms-dev
* liblcms-utils

.. _littleCMS: http://www.littlecms.com/


Install Transmogrify
====================

Create a "home" for transmogrify

.. code-block:: console

   # mkdir -p /etc/transmogrify
   # cd /etc/transmogrify

Download and run the bootstrap program:

.. code-block:: console

   # curl https://raw.github.com/callowayproject/Transmogrify/master/bootstrap.py | python

You can install the latest development release using this command:

.. code-block:: console

   # curl https://raw.github.com/callowayproject/Transmogrify/master/bootstrap.py --dev | python


These create a python ``virtualenv`` and installs Transmogrify.


Create settings file
====================

#. Execute ``source virtualenv/bin/activate`` to activate the Transmogrify's virtualenv.

#. Execute ``configure_transmogrify``

#. Answer the questions.

.. code-block:: console

   Specify your Secret Key, or use this random key [p9pmpo)-l@c=ux06#ucezz@t4f1j6*_re%-area6xk&_ic#u0r]:
   Where are your original files stored [/etc/transmogrify/originals]:
   Where will your modified files be stored [/etc/transmogrify/modified]:
   Where would you like to store the settings [transmogrify_settings.py]:


Install OpenCV
==============

#. Execute ``source virtualenv/bin/activate`` to activate the Transmogrify's virtualenv.

#. I'm using instructions found at http://karytech.blogspot.com/2012/05/opencv-24-on-ubuntu-1204.html to install the latest version.

Install WSGI server
===================

Gunicorn
--------


uWSGI
-----

