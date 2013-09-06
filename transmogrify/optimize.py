import os
try:
    from PIL import Image
    from PIL.ImageCms import profileToProfile
except ImportError:
    profileToProfile = lambda im, *args, **kwargs: im


def convert_to_RGB(img):
    """
    Convert an image to RGB if it isn't already RGB or grayscale
    """
    inputProfile = "/Users/coordt/Downloads/Adobe ICC Profiles/CMYK Profiles/USWebUncoated.icc"
    outputProfile = "/Users/coordt/Downloads/sRGB_v4_ICC_preference.icc"
    if img.mode not in ('RGB', 'L'):
        return profileToProfile(img, inputProfile, outputProfile, outputMode='RGB')
    return img


def get_output_filename(input_filename):
    parent_dir, filename = os.path.split(input_filename)
    base_filename, ext = os.path.splitext(filename)
    return os.path.join("/Users/coordt/Desktop", "%s.optim%s" % (base_filename, ext))


def main():
    input_filename = "/Users/coordt/Desktop/pumpkin_632716265.jpg"
    output_filename = get_output_filename(input_filename)
    original = Image.open(input_filename)
    modified = convert_to_RGB(original)
    modified.save(output_filename, optimized=True, progressive=True)
