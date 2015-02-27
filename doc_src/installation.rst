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

Example:

.. code-block:: console

   # sudo apt-get install python-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk


Install Transmogrify
====================

Create a "home" for transmogrify

.. code-block:: console

   # mkdir -p /etc/transmogrify
   # cd /etc/transmogrify

Download the setuptools and pip wheels

.. code-block:: console

   # mkdir virtualenv_support
   # cd virtualenv_support/
   # sudo wget https://pypi.python.org/packages/py2.py3/p/pip/pip-1.5.6-py2.py3-none-any.whl#md5=4d4fb4b69df6731c7aeaadd6300bc1f2
   # sudo wget https://pypi.python.org/packages/3.4/s/setuptools/setuptools-8.2-py2.py3-none-any.whl#md5=44a36e437d09e3eb125a14c3a428b0f8
   # cd ..

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

#. Make a file called ``/etc/transmogrify/conf/gunicorn_conf.py``

   .. code-block:: python

       NAME = 'transmogrify'
       bind = "unix:///var/run/%s.sock" % NAME
       pidfile = "/var/run/%s.pid" % NAME
       user = "www-data"
       group = "www-data"
       accesslog = "/var/log/gunicorn/%s.access.log" % NAME
       errorlog = "/var/log/gunicorn/%s.error.log" % NAME
       proc_name = NAME

#. Create a script called ``/etc/transmogrify/transmogrify``

   .. code-block:: bash

       #!/bin/bash
       HOMEDIR="/etc/transmogrify"
       CONF="$HOMEDIR/conf/gunicorn_conf.py"
       NAME=transmogrify
       cd $HOMEDIR
       source virtualenv/bin/activate
       TRANSMOGRIFY_SETTINGS=transmogrify_settings exec $HOMEDIR/virtualenv/bin/python \
          /etc/transmogrify/virtualenv/bin/gunicorn \
          --config $CONF transmogrify.wsgi:app

#. Make the script executable

   .. code-block:: console

      # chmod a+x transmogrify

#. Make a startup script (this is an Ubuntu upstart script: ``/etc/init/transmogrify.conf``\ )

   .. code-block:: bash

      description "Transmogrify"
      start on runlevel [2345]
      stop on runlevel [06]
      respawn
      respawn limit 10 5

      script
          /etc/transmogrify/transmogrify
      end script

#. Make a webserver configuration (this is an nGinx config: ``/etc/nginx/sites-available/transmogrify``\ )

   .. code-block

      server {
          listen          80;
          server_name     media.example.com;
          access_log      off;
          log_not_found   off;
          error_log       /var/log/nginx/transmogrify.error.log;
          error_page 404 = @transmogrify_proxy;
          client_max_body_size  30M;

          location /assets/ {
              alias       /etc/transmogrify/modified/;
              expires     7d;
              add_header  pragma public;
              add_header  cache-control "public";
          }
          location /static/ {
              alias       /etc/transmogrify/static/;
              expires     7d;
              add_header  pragma public;
              add_header  cache-control "public";
          }
          location /uploads/ {
              alias       /etc/transmogrify/uploads/;
              expires     7d;
              add_header  pragma public;
              add_header  cache-control "public";
          }
          location /favicon.ico {
              alias       /etc/transmogrify/static/favicon.ico;
              expires     7d;
              add_header  pragma public;
              add_header  cache-control "public";
          }
          location @transmogrify_proxy {
              proxy_pass                  http://unix:///var/run/transmogrify.sock;
              proxy_redirect              off;
              proxy_set_header            Host $host;
              proxy_set_header            X-Real-IP $remote_addr;
              proxy_set_header            X-Forwarded-For $proxy_add_x_forwarded_for;
              client_max_body_size        1000m;
              client_body_buffer_size     128k;
              proxy_connect_timeout       90;
              proxy_send_timeout          90;
              proxy_read_timeout          90;
              proxy_buffer_size           4k;
              proxy_buffers               4 32k;
              proxy_busy_buffers_size     64k;
              proxy_temp_file_write_size  64k;
              expires                     0d;
          }
          gzip            on;
          gzip_disable    "msie6";
          gzip_types      text/plain text/css application/x-javascript
                          text/xml application/xml application/xml+rss
                          text/javascript;
          gzip_vary       on;
      }

uWSGI
-----



Change Permissions
==================

#. sudo chown -r www-data:www-data /etc/transmogrify
