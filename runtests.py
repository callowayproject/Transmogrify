#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    APP = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(APP)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'example.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["transmogrify"])
    sys.exit(bool(failures))
