import subprocess
import os

try:
    from PIL import Image
    from PIL.ImageCms import profileToProfile
except ImportError:
    profileToProfile = lambda im, *args, **kwargs: im  # NOQA

from .settings import IMAGE_OPTIMIZATION_CMD
from .utils import is_tool


def convert_to_rgb(img):
    """
    Convert an image to RGB if it isn't already RGB or grayscale
    """
    if img.mode not in ('RGB', 'L'):
        profile_dir = os.path.join(os.path.dirname(__file__), 'profiles')
        input_profile = os.path.join(profile_dir, "USWebUncoated.icc")
        output_profile = os.path.join(profile_dir, "sRGB_v4_ICC_preference.icc")
        return profileToProfile(img, input_profile, output_profile, outputMode='RGB')
    return img


def get_output_filename(input_filename):
    parent_dir, filename = os.path.split(input_filename)
    base_filename, ext = os.path.splitext(filename)
    return os.path.join(parent_dir, "%s.optim%s" % (base_filename, ext))


def optimize(image, fmt='jpeg', quality=80):
    """
    Optimize the image if the IMAGE_OPTIMIZATION_CMD is set.

    IMAGE_OPTIMIZATION_CMD must accept piped input
    """
    from io import BytesIO
    from PIL import Image

    if IMAGE_OPTIMIZATION_CMD and is_tool(IMAGE_OPTIMIZATION_CMD):
        image_buffer = BytesIO()
        image.save(image_buffer, format=fmt, quality=quality)
        p1 = subprocess.Popen([IMAGE_OPTIMIZATION_CMD], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output_optim, output_err = p1.communicate(image_buffer.read())
        im = Image.open(BytesIO(output_optim))
        return im
    else:
        return image


def test_rgb_conversion(input_filename):
    output_filename = get_output_filename(input_filename)
    original = Image.open(input_filename)
    modified = convert_to_rgb(original)
    modified.save(output_filename, optimized=True, progressive=True)
