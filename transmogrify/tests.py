import unittest
import os
from django.template import Template, Context
from StringIO import StringIO
import wsgi_handler
from transmogrify import Transmogrify
import utils
import settings
import shutil
import mock
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

    def testCropBBOX(self):
        expected_square = (300,300)
        transmog = Transmogrify(self.square_img, [('c', '100-100-400-400'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        transmog = Transmogrify(self.vert_img, [('c', '0-100-300-400'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        transmog = Transmogrify(self.horiz_img, [('c', '0-410-300-710'),])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        # 810 is larger than the image, PIL adds black to the extra space.
        # who knows if this is desirable but at least it doesn't raise
        # an exception.
        transmog = Transmogrify(self.horiz_img, [('c', '0-510-300-810'),])
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

class UrlProcessingTest(TestCase):
    """
    Test aspects of URL processing.
    """
    def doShaHash(self, value):
        import hashlib
        return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()
    
    def testAliases(self):
        import utils
        utils.PATH_ALIASES = {'/media/':'/testdata/'}
        utils.BASE_PATH = os.path.abspath(os.path.dirname(__file__))
        url = "/media/horiz_img_r200.jpg"
        url += "?%s" % self.doShaHash('_r200')
        result = utils.process_url(url)
        self.assertEquals(result['original_file'], os.path.join(utils.BASE_PATH, 'testdata', 'horiz_img.jpg'))

class TestMakeDirs(TestCase):
    def setUp(self):
        self.test_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'testdata', "makedirs"))

    def tearDown(self):
        dirs = [
            os.path.join(self.test_root, "didnotexist"),
            os.path.join(self.test_root, "partiallyexists", "foo", "bar"),
            ]

        for item in dirs:
            if os.path.exists(item):
                shutil.rmtree(item)
                         
    def test_didnotexist(self):
        path = os.path.join(self.test_root,
                            "didnotexist", "foo", "bar", "baz")
        wsgi_handler.makedirs(path)
        self.assertTrue(os.path.isdir(path))

    def test_exists(self):
        path = os.path.join(self.test_root,
                            "exists", "foo", "bar", "baz")
        wsgi_handler.makedirs(path)
        self.assertTrue(os.path.isdir(path))

    def test_partiallyexists(self):
        path = os.path.join(self.test_root,
                            "partiallyexists", "foo", "bar", "baz")
        wsgi_handler.makedirs(path)
        self.assertTrue(os.path.isdir(path))

    def test_nondirbit(self):
        path = os.path.join(self.test_root,
                            "nondirbit", "foo", "bar", "baz")

        self.assertRaises(OSError, wsgi_handler.makedirs, path)


class TestDoFallback(TestCase):
    def setUp(self):
        self.testdata_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata'))
        self.fallback_server = "http://i.usatoday.com/"

        self.base_path = self.testdata_root

        self.expected_url = \
            "http://i.usatoday.com/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg"

        self.path_info =\
            "life/gallery/2012/l120523_untamed/02untamed-pg-horizontal_r115.jpg"

        self.output_file = os.path.join(self.base_path,
            "life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg")

        # clean the slate
        self.tearDown()
        
    def tearDown(self):
        test_root = os.path.join(self.testdata_root, "life")
        if os.path.exists(test_root):
            shutil.rmtree(test_root)


    @mock.patch("shutil.move")
    @mock.patch("os.path.exists")
    @mock.patch("urllib.URLopener")
    def test_200(self, mock_opener, mock_exists, mock_move):
        ##
        # Setup mocks
        ##
        instance = mock_opener.return_value
        instance.retrieve.return_value = ("/tmp/sometmpfilename", mock.Mock())

        mock_exists.return_value = False

        ##
        # Execute
        ##
        success = wsgi_handler.do_fallback(self.fallback_server,
                                           self.base_path,
                                           self.path_info)

        ##
        # Test
        ##
        
        self.assertTrue(success)

        # Ensure that the URLopener instance was called with the
        # correct parameters
        instance.retrieve.assert_called_with(self.expected_url)

        # Ensure the directory tree was created.
        self.assertTrue(os.path.isdir(os.path.dirname(self.output_file)))
        
        # Ensure that shutil.move was called correctly
        mock_move.assert_called_with("/tmp/sometmpfilename", 
                                     self.output_file)

    @mock.patch("shutil.move")
    @mock.patch("os.path.exists")
    @mock.patch("urllib.URLopener")
    def test_non200(self, mock_opener, mock_exists, mock_move):
        ##
        # Setup mocks
        ##
        instance = mock_opener.return_value
        http_error = IOError('http error', 404, 'NOT FOUND', mock.Mock())
        instance.retrieve.side_effect = http_error
        mock_exists.return_value = False

        ##
        # Execute
        ##
        result = wsgi_handler.do_fallback(self.fallback_server,
                                          self.base_path,
                                          self.path_info)


        # assert that do_fallback did not create the
        # object and the reason was because of the http_error
        self.assertEqual((False, http_error), result)
        
        # Ensure the directory tree was not created.
        self.assertTrue(
            not os.path.isdir(os.path.dirname(self.output_file)),
            os.path.dirname(self.output_file))
        
        # Ensure that the URLopener instance was called with the
        # correct parameters
        instance.retrieve.assert_called_with(self.expected_url)

        # Ensure that the move never happend
        self.assertFalse(mock_move.called)

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
                'wsgi.input': StringIO(),
            }
            environ.update(self.defaults)
            environ.update(request)
            return WSGIRequest(environ)
    
    class TemplateTagTest(TestCase):
        def doShaHash(self, value):
            import hashlib
            return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()
        
        def testResize(self):
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_r300.jpg?%s' % self.doShaHash("_r300"))
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg x300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_rx300.jpg?%s' % self.doShaHash("_rx300"))
            t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_r300x300.jpg?%s' % self.doShaHash("_r300x300"))

        def testForceFit(self):
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_s300.jpg?%s' % self.doShaHash("_s300"))
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg x300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_sx300.jpg?%s' % self.doShaHash("_sx300"))
            t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_s300x300.jpg?%s' % self.doShaHash("_s300x300"))
        
        def testCrop(self):
            t = Template("{% load transmogrifiers %}{% crop /test/picture.jpg 300x300 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_c300x300.jpg?%s' % self.doShaHash("_c300x300"))

        def testCropBBox(self):
            t = Template("{% load transmogrifiers %}{% crop /test/picture.jpg 0-0-100-100 %}")
            self.assertEqual(t.render(Context({})), '/test/picture_c0-0-100-100.jpg?%s' % self.doShaHash("_c0-0-100-100"))
        
        def testLetterbox(self):
            t = Template("{% load transmogrifiers %}{% letterbox /test/picture.jpg 300x300 #f8129b  %}")
            self.assertEqual(t.render(Context({})), '/test/picture_l300x300-f8129b.jpg?%s' % self.doShaHash("_l300x300-f8129b"))
        
        def testBorder(self):
            t = Template("{% load transmogrifiers %}{% border /test/picture.jpg 1 #f8129b %}")
            self.assertEqual(t.render(Context({})), '/test/picture_b1-f8129b.jpg?%s' % self.doShaHash("_b1-f8129b"))

        def testExistingActionString(self):
            t = Template("{% load transmogrifiers %}{% resize /test/picture_c0-0-300-300.jpg 300x300 %}")
            self.assertEqual(t.render(Context({})), u'/test/picture_c0-0-300-300_r300x300.jpg?%s' % self.doShaHash("_c0-0-300-300_r300x300"))

        def testMask(self):
            t = Template("{% load transmogrifiers %}{% mask /test/picture.jpg %}")
            self.assertEqual(t.render(Context({})), u'/test/picture_m.jpg?%s' % self.doShaHash("_m"))
            

    class TemplateFilterTest(TestCase):
        def doShaHash(self, value):
            import hashlib
            return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()
        
        def testResize(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|resize:"300" }}')
            self.assertEqual(t.render(context), '/test/picture_r300.jpg?%s' % self.doShaHash("_r300"))
            t = Template('{% load transmogrifiers %}{{ img_url|resize:"x300" }}')
            self.assertEqual(t.render(context), '/test/picture_rx300.jpg?%s' % self.doShaHash("_rx300"))
            t = Template('{% load transmogrifiers %}{{ img_url|resize:"300x300" }}')
            self.assertEqual(t.render(context), '/test/picture_r300x300.jpg?%s' % self.doShaHash("_r300x300"))

        def testForceFit(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"300" }}')
            self.assertEqual(t.render(context), '/test/picture_s300.jpg?%s' % self.doShaHash("_s300"))
            t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"x300" }}')
            self.assertEqual(t.render(context), '/test/picture_sx300.jpg?%s' % self.doShaHash("_sx300"))
            t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"300x300" }}')
            self.assertEqual(t.render(context), '/test/picture_s300x300.jpg?%s' % self.doShaHash("_s300x300"))
        
        def testCrop(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|crop:"300x300" }}')
            self.assertEqual(t.render(context), '/test/picture_c300x300.jpg?%s' % self.doShaHash("_c300x300"))

        def testCropBBox(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|crop:"0-0-100-100" }}')
            self.assertEqual(t.render(context), '/test/picture_c0-0-100-100.jpg?%s' % self.doShaHash("_c0-0-100-100"))
        
        def testLetterbox(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|letterbox:"300x300 #f8129b" }}')
            self.assertEqual(t.render(context), '/test/picture_l300x300-f8129b.jpg?%s' % self.doShaHash("_l300x300-f8129b"))
        
        def testBorder(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|border:"1 #f8129b" }}')
            self.assertEqual(t.render(context), '/test/picture_b1-f8129b.jpg?%s' % self.doShaHash("_b1-f8129b"))

        def testMask(self):
            context = Context({"img_url": "/test/picture.jpg"})

            t = Template('{% load transmogrifiers %}{{ img_url|mask }}')
            self.assertEqual(t.render(context), '/test/picture_m.jpg?%s' % self.doShaHash("_m"))
    
        def testChaining(self):
            context = Context({"img_url": "/test/picture.jpg"})
            t = Template('{% load transmogrifiers %}{{ img_url|crop:"0-0-300-300"|resize:"x100" }}')
            self.assertEqual(t.render(context), '/test/picture_c0-0-300-300_rx100.jpg?%s' % self.doShaHash("_c0-0-300-300_rx100"))
            
        def testExistingActionString(self):
            context = Context({"img_url": "/test/picture_c0-0-300-300.jpg"})
            t = Template('{% load transmogrifiers %}{{ img_url|resize:"x100" }}')
            self.assertEqual(t.render(context), '/test/picture_c0-0-300-300_rx100.jpg?%s' % self.doShaHash("_c0-0-300-300_rx100"))


    class ViewTest(TestCase):
        def doShaHash(self, value):
            import hashlib
            return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()
        
        def testView(self):
            rf = RequestFactory()
            path = '/horiz_img_r300x400.jpg'
            document_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata'))
            request = rf.get('%s?%s' % (path, self.doShaHash("_r300x400")))
            import views
            response = views.transmogrify_serve(request, path, document_root)
            self.assertEqual(response.status_code, 200)

    class TestUtil(unittest.TestCase):
        def testGenerateUrl(self):
            expected = ("http://example.com/media/foo_r200.jpg"
                        "?d7a3f8c02c4ecb0c13aa024e1d80d1053ad1deec")

            result = utils.generate_url("http://example.com/media/foo.jpg",
                                        "_r200")
            self.assertEqual(expected, result)

            
if __name__ == "__main__":
    unittest.main()
