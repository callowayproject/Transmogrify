from collections import namedtuple
from PIL import Image, ImageFilter, ImageChops
from .settings import OPENCV_PREFIX

try:
    import cv2
    import cv
    HAS_OPENCV = True
    DEFAULT_CASCADE_FN = '%sOpenCV/haarcascades/haarcascade_frontalface_default.xml' % OPENCV_PREFIX
    DEFAULT_FLAGS = cv.CV_HAAR_SCALE_IMAGE
except ImportError:
    HAS_OPENCV = False
    DEFAULT_CASCADE_FN = '%sOpenCV/haarcascades/haarcascade_frontalface_default.xml' % OPENCV_PREFIX
    DEFAULT_FLAGS = None


class Rect(namedtuple('Rect', ['left', 'top', 'right', 'bottom'])):
    @property
    def tl(self):
        return (self.left, self.top)

    @property
    def br(self):
        return (self.right, self.bottom)

    @property
    def center(self):
        x = self.left + ((self.right - self.left) / 2)
        y = self.top + ((self.bottom - self.top) / 2)
        return (x, y)


class CropInfo(object):
    def __init__(self, left=0, top=0, right=1, bottom=1, gravity=(.5, .5), relative=True):
        self.topleft = (left, top)
        self.bottomright = (bottom, right)
        self.gravity = gravity
        self.relative = relative
        self.calculated = True

    def to_relative(self, width, height):
        if self.relative:
            return self
        return CropInfo(
            left=self.topleft[0] / width,
            top=self.topleft[1] / height,
            right=self.bottomright[0] / width,
            bottom=self.bottomright[1] / height,
            gravity=(self.gravity[0] / width, self.gravity[1] / height)
        )

    def to_absolute(self, width, height):
        if not self.relative:
            return self
        return CropInfo(
            left=self.topleft[0] * width,
            top=self.topleft[1] * height,
            right=self.bottomright[0] * width,
            bottom=self.bottomright[1] * height,
            gravity=(self.gravity[0] * width, self.gravity[1] * height),
            relative=False
        )


if HAS_OPENCV:
    def find_faces(img_path, cascade_fn=DEFAULT_CASCADE_FN,
               scaleFactor=1.3, minNeighbors=4, minSize=(20, 20),
               flags=DEFAULT_FLAGS):
        img_color = cv2.imread(img_path)
        img_gray = cv2.cvtColor(img_color, cv.CV_BGR2GRAY)
        img_gray = cv2.equalizeHist(img_gray)
        cascade = cv2.CascadeClassifier(cascade_fn)
        rects = cascade.detectMultiScale(img_gray, scaleFactor=scaleFactor,
                                         minNeighbors=minNeighbors,
                                         minSize=minSize, flags=flags)

        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects

    def do_face_detection(img_path, cascade_fn=DEFAULT_CASCADE_FN,
               scaleFactor=1.3, minNeighbors=4, minSize=(20, 20),
               flags=DEFAULT_FLAGS):

        centers = []
        rects = find_faces(img_path, cascade_fn, scaleFactor, minNeighbors, minSize, flags)
        for rect in rects:
            centers.append(Rect(*rect).center)
        x = [x[0] for x in centers]
        y = [y[1] for y in centers]
        dims = cv2.imread(img_path).shape  # height, width, maybe color depth
        w = dims[1]
        h = dims[0]
        if centers:
            return ((sum(x) / len(x)) / float(w), (sum(y) / len(y)) / float(h))
        return []
else:
    def do_face_detection(*args, **kwargs):
        """
        Shim to handle when openCV isn't available. Just returns []
        """
        return []


def energy_center(image):
    width, height = image.size
    if not image.mode == 'L':
        temp_image = image.convert('L', (0.5, 0.419, 0.081, 0))
    else:
        temp_image = image.copy()
    min_val, max_val = temp_image.getextrema()
    threshold = min(max(0, max_val - 1), 200)
    accum = 0
    accumX = 0
    accumY = 0
    dvalue = 0
    for y in range(height):
        for x in range(width):
            value = temp_image.getpixel((x, y))
            if value > threshold:
                value -= threshold
                dvalue = (value * value) / float(255 * 255)
                accum += dvalue
                accumX += x * dvalue
                accumY += y * dvalue
    if accum:
        cx = accumX / accum
        cy = accumY / accum
    else:
        cx = width / 2
        cy = height / 2
    return (cx / float(width), cy / float(height))


def face_and_energy_detector(image_path, detect_faces=True):
    """
    Finds faces and energy in an image
    """
    source = Image.open(image_path)
    work_width = 800
    if source.mode != 'RGB' or source.bits != 8:
        source24 = source.convert('RGB')
    else:
        source24 = source.copy()

    grayscaleRMY = source24.convert('L', (0.5, 0.419, 0.081, 0))
    w = min(grayscaleRMY.size[0], work_width)
    h = w * grayscaleRMY.size[1] / grayscaleRMY.size[0]
    b = grayscaleRMY.resize((w, h), Image.BICUBIC)
    # b.save('step2.jpg')
    if detect_faces:
        info = do_face_detection(image_path)
        if info:
            return CropInfo(gravity=info)
    b = b.filter(ImageFilter.GaussianBlur(7))
    # b.save('step3.jpg')
    sobelXfilter = ImageFilter.Kernel((3, 3), (1, 0, -1, 2, 0, -2, 1, 0, -1), -.5)
    sobelYfilter = ImageFilter.Kernel((3, 3), (1, 2, 1, 0, 0, 0, -1, -2, -1), -.5)
    b = ImageChops.lighter(b.filter(sobelXfilter), b.filter(sobelYfilter))
    b = b.filter(ImageFilter.FIND_EDGES)
    # b.save('step4.jpg')
    ec = energy_center(b)
    return CropInfo(gravity=ec)


def get_crop_size(crop_w, crop_h, image_w, image_h):
    """
    Determines the correct scale size for the image

    when img w == crop w and img h > crop h
        Use these dimensions

    when img h == crop h and img w > crop w
        Use these dimensions
    """
    scale1 = float(crop_w) / float(image_w)
    scale2 = float(crop_h) / float(image_h)
    scale1_w = crop_w  # int(round(img_w * scale1))
    scale1_h = int(round(image_h * scale1))
    scale2_w = int(round(image_w * scale2))
    scale2_h = crop_h  # int(round(img_h * scale2))

    if scale1_h > crop_h:  # scale1_w == crop_w
        # crop on vertical
        return (scale1_w, scale1_h)
    else:  # scale2_h == crop_h and scale2_w > crop_w
        #crop on horizontal
        return (scale2_w, scale2_h)


def calc_subrange(range_max, sub_amount, weight):
    """
    return the start and stop points that are sub_amount distance apart and
    contain weight, without going outside the provided range
    """
    if weight > range_max or sub_amount > range_max:
        raise ValueError("sub_amount and weight must be less than range_max. range_max %s, sub_amount %s, weight %s" % (range_max, sub_amount, weight))
    half_amount = sub_amount / 2
    bottom = weight - half_amount
    top = bottom + sub_amount
    if top <= range_max and bottom >= 0:
        return (bottom, top)
    elif weight > range_max / 2:
        # weight is on the upper half, start at the max and go down
        return (range_max - sub_amount, range_max)
    else:
        # weight is on the lower have, start at 0 and go up
        return (0, sub_amount)


def smart_crop(crop_w, crop_h, image_path):
    """
    Return the scaled image size and crop rectangle
    """
    cropping = face_and_energy_detector(image_path)
    img = Image.open(image_path)
    w, h = img.size
    scaled_size = get_crop_size(crop_w, crop_h, *img.size)
    gravity_x = int(round(scaled_size[0] * cropping.gravity[0]))
    gravity_y = int(round(scaled_size[1] * cropping.gravity[1]))
    if scaled_size[0] == crop_w:
        # find the top and bottom crops
        crop_top, crop_bot = calc_subrange(scaled_size[1], crop_h, gravity_y)
        return scaled_size, Rect(left=0, top=crop_top, right=crop_w, bottom=crop_bot)
    else:
        # find the right and left crops
        crop_left, crop_right = calc_subrange(scaled_size[0], crop_w, gravity_x)
        return scaled_size, Rect(left=crop_left, top=0, right=crop_right, bottom=crop_h)
