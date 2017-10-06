import os
# import pytest

from transmogrify.autodetect import smart_crop
from transmogrify.settings import ORIG_BASE_PATH


sc = smart_crop(800, 542, os.path.join(ORIG_BASE_PATH, '2188374.tif'))
