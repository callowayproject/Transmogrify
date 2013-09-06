"""
Point and Rectangle classes.

This code is in the public domain. Based on http://wiki.python.org/moin/PointsAndRectangles

Point -- point with (x,y) coordinates
Rect  -- two points, forming a rectangle
"""
import math
from collections import namedtuple


class Point(namedtuple('Point', ['x', 'y'])):
    """
    A point identified by (x,y) coordinates.

    supports: +, -, *, /, str, repr

    **length:** calculate length of vector to point from origin
    **distance_to:** calculate distance between two points
    **as_tuple:** construct tuple (x,y)
    **clone:** construct a duplicate
    **integerize:** convert x & y to integers
    **floatize:** convert x & y to floats
    **move_to:** reset x & y
    **translate:** move (in place) +dx, +dy, as spec'd by point
    **rotate:** rotate around the origin
    **rotate_about:** rotate around another point
    """
    def __eq__(self, other):
        return isinstance(other, Point) and other.x == self.x and other.y == self.y

    def __ne__(self, other):
        return not isinstance(other, Point) or other.x != self.x or other.y != self.y

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __int__(self):
        return Point(int(round(self.x)), int(round(self.y)))

    def __float__(self):
        return Point(float(self.x), float(self.y))

    def __add__(self, p):
        """
        Add either one point's coordinates to this one's, or add a value to both
        """
        if isinstance(p, Point):
            return Point(self.x + p.x, self.y + p.y)
        elif isinstance(p, (int, float)):
            return Point(self.x + p, self.y + p)
        else:
            return NotImplemented

    def __sub__(self, p):
        """
        Subtract either one point's coordinates to this one's, or subtract a
        value from both
        """
        if isinstance(p, Point):
            return Point(self.x - p.x, self.y - p.y)
        elif isinstance(p, (int, float)):
            return Point(self.x - p, self.y - p)
        else:
            return NotImplemented

    def __mul__(self, p):
        """
        Multiply a value to each dimension
        """
        if isinstance(p, Point):
            return Point(self.x * p.x, self.y * p.y)
        elif isinstance(p, (int, float)):
            return Point(self.x * p, self.y * p)
        else:
            return NotImplemented

    def __div__(self, p):
        """
        Divide a value into each dimension
        """
        if isinstance(p, Point):
            return Point(self.x / p.x, self.y / p.y)
        elif isinstance(p, (int, float)):
            return Point(self.x / p, self.y / p)
        else:
            return NotImplemented

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, p):
        """
        Calculate the distance between two points.
        """
        return (self - p).length()

    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)

    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)

    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(round(self.x))
        self.y = int(round(self.y))

    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)

    def move_to(self, x, y):
        """
        Reset x & y coordinates.
        """
        self.x = x
        self.y = y

    def translate(self, val1, val2=None):
        """
        Move to new (x + dx, y + dy).

        accepts Point, (x, y), [x, y], int, float
        """
        error = "Point.translate only accepts a Point, a tuple, a list, ints or floats."
        if val1 and val2:
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                self.x += val1
                self.y += val2
            else:
                raise ValueError(error)
        elif val1 and val2 is None:
            if isinstance(val1, (tuple, list)):
                self.x += val1[0]
                self.y += val1[1]
            elif isinstance(val1, (int, float)):
                self.x += val1
                self.y += val1
            elif isinstance(val1, Point):
                self.x += val1.x
                self.y += val1.y
            else:
                raise ValueError(error)
        else:
            raise ValueError(error)

    def rotate(self, rad):
        """
        Rotate counter-clockwise by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        """
        Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.
        """
        result = self.clone()
        result.translate(-p.x, -p.y)
        result.rotate(theta)
        result.translate(p.x, p.y)
        return result


class Rect(namedtuple('Rect', ['left', 'top', 'right', 'bottom'])):
    """
    A rectangle identified by two points.

    The rectangle stores left, top, right, and bottom values.

    Coordinates are based on screen coordinates.

    origin                               top
       +-----> x increases                |
       |                           left  -+-  right
       v                                  |
    y increases                         bottom

    set_points  -- reset rectangle coordinates
    contains  -- is a point inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    expanded_by  -- grow (or shrink)
    """
    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        (x1, y1) = pt1.as_tuple()
        (x2, y2) = pt2.as_tuple()
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)

    def __contains__(self, pt):
        """Return true if a point is inside the rectangle."""
        if isinstance(pt, Point):
            x, y = pt.as_tuple()
            return (self.left <= x <= self.right and
                    self.top <= y <= self.bottom)
        elif isinstance(pt, Rect):
            return (
                (self.left <= pt.left <= self.right and
                 self.top <= pt.top <= self.bottom) and
                (self.left <= pt.right <= self.right and
                 self.top <= pt.bottom <= self.bottom))
        else:
            return NotImplemented

    def overlaps(self, other):
        """
        Return true if a rectangle overlaps this rectangle.
        """
        return (
            self.right > other.left and
            self.left < other.right and
            self.top < other.bottom and
            self.bottom > other.top
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def top_left(self):
        """Return the top-left corner as a Point."""
        return Point(self.left, self.top)

    @property
    def tl(self):
        """Return the top-left corner as a Point."""
        return Point(self.left, self.top)

    @property
    def bottom_right(self):
        """Return the bottom-right corner as a Point."""
        return Point(self.right, self.bottom)

    @property
    def br(self):
        """Return the bottom-right corner as a Point."""
        return Point(self.right, self.bottom)

    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        return Rect(self.left - n, self.top - n, self.right + n, self.bottom + n)

    def __str__(self):
        return "<Rect (%s,%s)-(%s,%s)>" % (self.left, self.top,
                                           self.right, self.bottom)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                               Point(self.left, self.top),
                               Point(self.right, self.bottom))
