import unittest
import os
from django.template import Template

from transmogrify import Transmogrify
from PIL import Image
try:
    from django.test import TestCase
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

class TestTransmogrify(unittest.TestCase):
    """Testing the features of Transmogrify"""
    def setUp(self):
        self.square_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'square_img.jpg'))
        self.vert_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'vert_img.jpg'))
        self.horiz_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'horiz_img.jpg'))
    
    def testThumbnail(self):
        expected_square = (300,300)
        expected_vert = (168,300)
        expected_horiz = (300,208)
        transmog = Transmogrify(self.square_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(self.horiz_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)
    
    def testResize(self):
        expected_square = (300,300)
        expected_vert = (168,300)
        expected_horiz = (300,208)
        transmog = Transmogrify(self.square_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(self.horiz_img, [('r', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)
    
    def testForceFit(self):
        expected_square = (300,300)
        transmog = Transmogrify(self.square_img, [('s', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('s', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.horiz_img, [('s', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
    
    def testCrop(self):
        expected_square = (300,300)
        transmog = Transmogrify(self.square_img, [('c', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('c', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.horiz_img, [('c', '300x300'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
    
    def testLetterbox(self):
        transmog = Transmogrify(self.square_img, [('l', '300x300-888'),])
        transmog.save()
        transmog = Transmogrify(self.vert_img, [('l', '300x300-888'),])
        transmog.save()
        transmog = Transmogrify(self.horiz_img, [('l', '300x300-888'),])
        transmog.save()
    
    def testBorder(self):
        transmog = Transmogrify(self.square_img, [('b', '3-f00'),])
        transmog.save()
        transmog = Transmogrify(self.vert_img, [('b', '3-f00'),])
        transmog.save()
        transmog = Transmogrify(self.horiz_img, [('b', '3-f00'),])
        transmog.save()

if HAS_DJANGO:
    # Note: By default the secret key is empty, so we can test just a straight
    # SHA1 hash of the action
    from django.test import Client
    from django.core.handlers.wsgi import WSGIRequest

    class RequestFactory(Client):
        """
        Class that lets you create mock Request objects for use in testing.

        Usage:

        rf = RequestFactory()
        get_request = rf.get('/hello/')
        post_request = rf.post('/submit/', {'foo': 'bar'})

        This class re-uses the django.test.client.Client interface, docs here:
        http://www.djangoproject.com/documentation/testing/#the-test-client

        Once you have a request object you can pass it to any view function, 
        just as if that view had been hooked up using a URLconf.

        """
        def request(self, **request):
            """
            Similar to parent class, but returns the request object as soon as it
            has created it.
            """
            environ = {
                'HTTP_COOKIE': self.cookies,
                'PATH_INFO': '/',
                'QUERY_STRING': '',
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': '',
                'SERVER_NAME': 'testserver',
                'SERVER_PORT': 80,
                'SERVER_PROTOCOL': 'HTTP/1.1',
            }
            environ.update(self.defaults)
            environ.update(request)
            return WSGIRequest(environ)
    
    class TemplateTagTest(TestCase):
        def doShaHash(self, value):
            import hashlib
            return hashlib.sha1(value).hexdigest()
        
        def testResize(self):
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300 %}")
            self.assertEqual(t.render({}), '/test/picture_r300.jpg?%s' % self.doShaHash("_r300"))
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg x300 %}")
            self.assertEqual(t.render({}), '/test/picture_rx300.jpg?%s' % self.doShaHash("_rx300"))
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render({}), '/test/picture_r300x300.jpg?%s' % self.doShaHash("_r300x300"))
        
        def testForceFit(self):
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300 %}")
            self.assertEqual(t.render({}), '/test/picture_s300.jpg?%s' % self.doShaHash("_s300"))
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg x300 %}")
            self.assertEqual(t.render({}), '/test/picture_sx300.jpg?%s' % self.doShaHash("_sx300"))
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render({}), '/test/picture_s300x300.jpg?%s' % self.doShaHash("_s300x300"))
        
        def testCrop(self):
            t = Template("{% load transmogrifiers %}{% crop /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render({}), '/test/picture_c300x300.jpg?%s' % self.doShaHash("_c300x300"))
        
        def testLetterbox(self):
            t = Template("{% load transmogrifiers %}{% letterbox /test/picture.jpg 300x300 #f8129b  %}")
            self.assertEqual(t.render({}), '/test/picture_l300x300-f8129b.jpg?%s' % self.doShaHash("_l300x300-f8129b"))
        
        def testBorder(self):
            t = Template("{% load transmogrifiers %}{% border /test/picture.jpg 1 #f8129b %}")
            self.assertEqual(t.render({}), '/test/picture_b1-f8129b.jpg?%s' % self.doShaHash("_b1-f8129b"))
    
    class ViewTest(TestCase):
        def doShaHash(self, value):
            import hashlib
            return hashlib.sha1(value).hexdigest()
        
        def testView(self):
            rf = RequestFactory()
            path = '/horiz_img_r300x400.jpg'
            document_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata'))
            request = rf.get('%s?%s' % (path, self.doShaHash("_r300x400")))
            import views
            response = views.transmogrify_serve(request, path, document_root)
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()