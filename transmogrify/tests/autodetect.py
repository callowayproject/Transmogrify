import autodetect
import cv2
import os

path = os.path.dirname(__file__)
cascades = [
    os.path.join(path, 'haarcascades', 'haarcascade_frontalface_alt.xml'),
    os.path.join(path, 'haarcascades', 'haarcascade_frontalface_alt2.xml'),
    os.path.join(path, 'haarcascades', 'haarcascade_frontalface_alt_tree.xml'),
    os.path.join(path, 'haarcascades', 'haarcascade_frontalface_default.xml'),
    os.path.join(path, 'haarcascades', 'haarcascade_profileface.xml'),
]


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def demo(in_fn, out_fn, cascade):
    rects = []
    for i in cascade:
        rects.extend(autodetect.find_faces(in_fn, cascade_fn=i))
    centers = []
    for rect in rects:
        centers.append(autodetect.Rect(*rect).center)
    x = [x[0] for x in centers]
    y = [y[1] for y in centers]
    # dims = cv2.imread(in_fn).shape  # height, width, maybe color depth
    # w = dims[1]
    # h = dims[0]
    if len(centers) == 0:
        print "No Faces detected"
        return
    gravity = (sum(x) / len(x), sum(y) / len(y))

    img_out = cv2.imread(in_fn).copy()
    draw_rects(img_out, rects, (0, 255, 0))
    cv2.circle(img_out, gravity, 5, (255, 255, 0), -1)
    cv2.imwrite(out_fn, img_out)


def main():
    img_path = '/Users/coordt/Desktop/accent-to-the-top_w725_h483.jpg'
    path, filename = os.path.split(img_path)
    name, ext = os.path.splitext(filename)
    out_path = "%s/%s_frontalface_all%s" % (path, name, ext)
    print out_path
    demo(img_path, out_path, cascades)


if __name__ == '__main__':
    main()
