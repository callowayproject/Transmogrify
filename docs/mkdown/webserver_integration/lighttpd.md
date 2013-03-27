Lighttpd Integration &mdash; Transmogrify v0.1beta2 documentation
# Lighttpd Integration #
<p>The easiest method to integrate Transmogrify into a Lighttpd server is as a server.error-handler-404. This allows Lighttpd to handle normal file serving, unless lighttpd can&#8217;t find the requested file. At that point, Lighttpd will pass off control to the script, which will either create the file and let Lighttpd serve it or return a 404 error. From that point on Lighttpd will be able to serve the file normally.</p>


## lighttpd.conf ##
<p>In your lighttpd.conf, you&#8217;ll need mod_cgi and mod_setenv in your server.modules:</p>

        server.modules = (
            ...
            "mod_cgi",
            "mod_setenv",
        )

<p>The .py extension must be assigned as cgi script:</p>

        cgi.assign = (".py" => "/usr/bin/python")

<p>Then the error handler is set. The value set is a URL, not a path. Unless you are going to put the python file in the server.document-root, you will have to do some configuring.</p>
<p>First decide where you are going to install the handler. For this example, the entire module is installed in python&#8217;s site-packages, and the actual error handling script (404_handler.py) is in /var/www/scripts/. So we&#8217;ll add an alias for this:</p>

        alias.url = (
            ...
            "/error/" => "/var/www/scripts/",
        )

<p>Now we can set the actual error handler:</p>

	server.error-handler-404 = &quot;/error/404_handler.py&quot;

<p>Lastly, we must configure a few parameters. These settings allow easy customization without having to customize the scripts. See Settings for details on each setting. There are a few more settings than shown in this example, but this is typical.</p>

        setenv.add-environment = (
            "TRANSMOGRIFY_KEY"  => "Anything you want, but keep it secret",
            "TRANSMOGRIFY_DEBUG" => "0",
            "TRANSMOGRIFY_ROOT" => "/web-media/export/assets/",
            "TRANSMOGRIFY_VHOSTS" => "0",
        )

## The 404 handler script ##
<p>The 404 handling script is pretty basic. It should look like:</p>

	from transmogrify import lighttpd_404_handler
        if __name__ == '__main__':
            lighttpd_404_handler.handle_request()

<p>Save that file as /var/www/scripts/404_handler.py and make sure the lighttpd process can read it.</p>


## Debugging the 404 Handler ##
<p>Figuring out what is going on with the 404 handler can be infuriating. Here are a few tips.</p>
* Make sure the TRANSMOGRIFY_DEBUG setting is 1. The error messages will be more detailed and a stacktrace will be returned if there was an internal error.
* Call the script from the shell. Some errors, such as ImportErrors simply fail without notice. Simply typing python /var/www/scripts/404_handler.py can show those errors.
* Check permissions. Make sure the web process can make new files where it is trying to make new files.
