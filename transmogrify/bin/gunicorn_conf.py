import os


def num_cpus():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

NAME = 'transmogrify'
workers = num_cpus() * 2 + 1

bind = "unix:///var/run/%s.sock" % NAME
pidfile = "/tmp/%s.pid" % NAME
user = "www-data"
group = "www-data"
accesslog = "/var/log/gunicorn/%s.access.log" % NAME
errorlog = "/var/log/gunicorn/%s.error.log" % NAME
proc_name = NAME
