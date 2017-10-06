import os
# import pytest

from transmogrify import optimize, settings, utils


def test_convert_to_rgb():
    """
    Test that an image gets converted from CMYK to RGB
    """
    from PIL import Image

    img = Image.open(os.path.join(settings.ORIG_BASE_PATH, '2188374.tif'))
    assert img.mode == 'CMYK'
    new_img = optimize.convert_to_rgb(img)
    assert new_img.mode == 'RGB'
    another_new_img = optimize.convert_to_rgb(new_img)
    assert another_new_img.mode == 'RGB'


def test_optimize():
    """
    Test that our mocked optimization tool goes through
    """
    from PIL import Image

    assert utils.is_tool(settings.IMAGE_OPTIMIZATION_CMD)

    img = Image.open(os.path.join(settings.ORIG_BASE_PATH, 'horiz_img.jpg'))

    new_img = optimize.optimize(img)
    assert img.size == new_img.size
