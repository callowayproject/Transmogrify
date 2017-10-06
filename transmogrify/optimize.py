import subprocess
import os
import logging
import daiquiri

try:
    from PIL import Image
    from PIL.ImageCms import profileToProfile
    HAS_PROFILE_TO_PROFILE = True
except ImportError:  # pragma: no cover
    HAS_PROFILE_TO_PROFILE = False

from .settings import IMAGE_OPTIMIZATION_CMD
from .utils import is_tool

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def convert_to_rgb(img):
    """
    Convert an image to RGB if it isn't already RGB or grayscale
    """
    if img.mode == 'CMYK' and HAS_PROFILE_TO_PROFILE:
        profile_dir = os.path.join(os.path.dirname(__file__), 'profiles')
        input_profile = os.path.join(profile_dir, "USWebUncoated.icc")
        output_profile = os.path.join(profile_dir, "sRGB_v4_ICC_preference.icc")
        return profileToProfile(img, input_profile, output_profile, outputMode='RGB')
    return img


def optimize(image, fmt='jpeg', quality=80):
    """
    Optimize the image if the IMAGE_OPTIMIZATION_CMD is set.

    IMAGE_OPTIMIZATION_CMD must accept piped input
    """
    from io import BytesIO

    if IMAGE_OPTIMIZATION_CMD and is_tool(IMAGE_OPTIMIZATION_CMD):
        image_buffer = BytesIO()
        image.save(image_buffer, format=fmt, quality=quality)
        image_buffer.seek(0)  # If you don't reset the file pointer, the read command returns an empty string
        p1 = subprocess.Popen(IMAGE_OPTIMIZATION_CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output_optim, output_err = p1.communicate(image_buffer.read())
        if not output_optim:
            logger.debug("No image buffer received from IMAGE_OPTIMIZATION_CMD")
            logger.debug("output_err: {0}".format(output_err))
            return image
        im = Image.open(BytesIO(output_optim))
        return im
    else:
        return image
