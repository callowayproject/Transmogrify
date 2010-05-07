from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
import re

SIZE_RE = re.compile(r"^((\d+)|(x\d+)|(\d+x\d+))$")

__all__ = ["Thumbnail", "Crop", "ForceFit", "Resize", "LetterboxResize", "Border", "Filter"]

class Processor(object):
    """
    The base class for image transformations
    """
    @staticmethod
    def code():
        return "z"
    
    @staticmethod
    def param_pattern():
        return re.compile(r'^(.*)$')
    
    @staticmethod
    def process(image, *args, **kwargs):
        return image
    
    @staticmethod
    def parse_size(image, size):
        """
        Parse a size string (i.e. "200", "200x100", "x200", etc.) into a (width,
        height) tuple. 
        """
        bits = size.split("x")
        if len(bits) == 1 or not bits[1]:
            width = int(bits[0])
            height = image.size[1]
        elif not bits[0]:
            height = int(bits[1])
            width = image.size[0]
        else:
            width, height = map(int, bits)
        return width, height
    
    @staticmethod
    def smart_fit(image, fit_to_width, fit_to_height):
        """
        Proportionally fit the image into the specified width and height. Return
        the correct width and height.
        """
        im_width, im_height = image.size
        out_width, out_height = fit_to_width, fit_to_height
        w_scale = float(fit_to_width)/float(im_width)
        h_scale = float(fit_to_height)/float(im_height)
        if w_scale < h_scale:
            scale = float(fit_to_width)/float(im_width)
            out_height = int(round(scale * im_height))
        else:
            scale = float(fit_to_height)/float(im_height)
            out_width = int(round(scale * im_width))
        
        return out_width, out_height


class Thumbnail(Processor):
    """
    Create a thumbnail at the specified size
    """
    @staticmethod
    def code():
        return "t"
    
    @staticmethod
    def param_pattern():
        return SIZE_RE
    
    @staticmethod
    def process(image, size, *args, **kwargs):
        width, height = Thumbnail.parse_size(image, size)
        image.thumbnail((width, height), Image.ANTIALIAS)
        return image

class Crop(Processor):
    """
    Crop out a centered box in the existing image.
    
    The one argument in the param_string is the size
    """
    @staticmethod
    def code():
        return "c"
    
    @staticmethod
    def param_pattern():
        return SIZE_RE
    
    @staticmethod
    def process(image, size, *args, **kwargs):
        w, h = Crop.parse_size(image, size)
        left = (image.size[0] - w) / 2
        top  = (image.size[1] - h) / 2
        right = left + w
        bottom = top + h
        return image.crop((left, top, right, bottom))

class ForceFit(Processor):
    """
    Force an image to fit in the specified dimensions, disregarding aspect ratio
    
    The one argument in the param_string is the size
    """
    @staticmethod
    def code():
        return "s"
    
    @staticmethod
    def param_pattern():
        return SIZE_RE
    
    @staticmethod
    def process(image, size, *args, **kwargs):
        w, h = ForceFit.parse_size(image, size)
        return image.resize((w, h), Image.ANTIALIAS)


class Resize(Processor):
    """
    Fit an image into the specified size, maintaining aspect ratio.
    
    The param_string contains only the size
    """
    @staticmethod
    def code():
        return "r"
    
    @staticmethod
    def param_pattern():
        return SIZE_RE
    
    @staticmethod
    def process(image, size, *args, **kwargs):
        box_width, box_height = Resize.parse_size(image, size)
        img_width, img_height = Resize.smart_fit(image, box_width, box_height)
        
        return image.resize((img_width, img_height), Image.ANTIALIAS)


class LetterboxResize(Processor):
    """
    Fit an image into the specified size, maintaining aspect ratio. Fill 
    remaining space with a color.
    
    The param_string contains two arguments: size and color separated by a dash
    
    eg. 300x200-f00 for a 300 by 200 thumbnail image on a red background
    """
    @staticmethod
    def code():
        return "l"
    
    @staticmethod
    def param_pattern():
        return re.compile(r"^(\d+|x\d+|\d+x\d+)-([a-f0-9]+)$")
    
    @staticmethod
    def process(image, param_string, *args, **kwargs):
        size, color = param_string.split("-")
        box_width, box_height = LetterboxResize.parse_size(image, size)
        img_width, img_height = LetterboxResize.smart_fit(image, box_width, box_height)
        
        if img_width == box_width:
            h_offset = 0
            v_offset = int((box_height - img_height)/2.0)
        elif img_height == box_height:
            v_offset = 0
            h_offset = int((box_width - img_width)/2.0)
        
        background = Image.new('RGB', (box_width, box_height), "#%s" % color)
        background.paste(image.resize((img_width, img_height), Image.ANTIALIAS), (h_offset, v_offset))
        
        return background

class Border(Processor):
    """
    Draw a border around the image of a given width and color
    
    The param_string contains two arguments: width and color separated by a dash
    
    e.g. 1-000 is a 1 pixel black border
    """
    @staticmethod
    def code():
        return "b"
    
    @staticmethod
    def param_pattern():
        return re.compile(r"^(\d+)-([a-f0-9]+)$")
    
    @staticmethod
    def process(image, param_string, *args, **kwargs):
        width, color = param_string.split("-")
        
        border_width = int(width)
        color = "#%s" % color
        
        draw = ImageDraw.Draw(image)
        
        # The rectangle gets drawn *inside* the upper left, but *outside* the
        # lower right (why, eff-bot, why?), so we have to subtract the width 
        # from the bottom right point so that the border will be inside the
        # image's bounds. Also, we have to draw a line instead of a rectangle
        # because rects don't support the "width" argument.
        # Fun, eh?
        left, top = 0, 0
        right, bottom = image.size[0] - border_width, image.size[1] - border_width
        points = [(left, top), (right, top), (right, bottom), (left, bottom), (left, top)]
        draw.line(points, width=border_width, fill=color)
        
        # Freeing the draw object forces rendering of the image.
        del draw
        return image

class Filter(Processor):
    """
    Apply one or more filters to an image. Uses filters available to PIL.
    Such as:
    
    BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, 
    SMOOTH, SMOOTH_MORE, and SHARPEN
    """
    @staticmethod
    def code():
        return "f"
    
    @staticmethod
    def param_pattern():
        IMAGE_FILTERS = [o.lower() for o in dir(ImageFilter) if o == o.upper()]
        return re.compile('^(%s)$' % ("|".join(IMAGE_FILTERS)), re.I)
    
    @staticmethod
    def process(image, filter_name, *args, **kwargs):
        img_filter = getattr(ImageFilter, filter_name.upper(), None)
        if img_filter:
            return image.filter(img_filter)
        else:
            return image

