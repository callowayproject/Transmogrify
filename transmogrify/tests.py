import unittest
import os
from django.template import Template, Context
from StringIO import StringIO
import wsgi_handler
from transmogrify import Transmogrify
import processors
import utils
import urllib
import settings
import shutil
from webob import Request
import mock
from PIL import Image
try:
    from django.test import TestCase
    from django.template import Template, Context
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

HERE = os.path.abspath(os.path.dirname(__file__))

class TestParseActionTuples(unittest.TestCase):
    def test(self):
        self.assertEqual(
            ("c05-v2-final-orioles-12-x-large", []),
            utils.parse_action_tuples("c05-v2-final-orioles-12-x-large")
        )

        self.assertEqual(
            ("c05-v2-final-orioles-12-x-large", [("r", "100x100")]),
            utils.parse_action_tuples(
                "c05-v2-final-orioles-12-x-large_r100x100"
            )
        )

        self.assertEqual(
            ("final-orioles-12-x-large", [("r", "100x100")]),
            utils.parse_action_tuples("final-orioles-12-x-large_r100x100")
        )

        self.assertEqual(
            ("foo_bar", []),
            utils.parse_action_tuples("foo_bar")
        )

        self.assertEqual(
            ("foo_bar", [("r", "100")]),
            utils.parse_action_tuples("foo_bar_r100")
        )

        self.assertEqual(
            ("c1088", []),
            utils.parse_action_tuples("c1088")
        )

        self.assertEqual(
            ("c1088-1_1", []),
            utils.parse_action_tuples("c1088-1_1")
        )


        self.assertEqual(
            ("c1088", [("c", "0-0-100-100")]),
            utils.parse_action_tuples("c1088_c0-0-100-100")
        )


class TestParseSize(unittest.TestCase):
    def test(self):
        image = mock.Mock()
        image.size = [100, 200]

        self.assertEqual((200, 400),
                         processors.Processor.parse_size(image,
                                                         "200"))

        self.assertEqual((200, 400),
                         processors.Processor.parse_size(image,
                                                         "x400"))

        self.assertEqual((300, 400),
                         processors.Processor.parse_size(image,
                                                         "300x400"))


class TestTransmogrify(unittest.TestCase):
    """Testing the features of Transmogrify"""
    def setUp(self):
        self.square_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'square_img.jpg'))
        self.vert_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'vert_img.jpg'))
        self.horiz_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'horiz_img.jpg'))
        self.cropname_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata', 'horiz_img-cropped.jpg'))

    def testThumbnail(self):
        expected_square = (300, 300)
        expected_vert = (168, 300)
        expected_horiz = (300, 208)
        transmog = Transmogrify(self.square_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(self.horiz_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)

    def testResize(self):
        expected_square = (300, 300)
        expected_vert = (168, 300)
        expected_horiz = (300, 208)
        transmog = Transmogrify(self.square_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(self.horiz_img, [('r', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)

    def testForceFit(self):
        expected_square = (300, 300)
        transmog = Transmogrify(self.square_img, [('s', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('s', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.horiz_img, [('s', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

    def testCrop(self):
        expected_square = (300, 300)
        transmog = Transmogrify(self.square_img, [('c', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.vert_img, [('c', '300x300'), ])
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(self.horiz_img, [('c', '300x300'), ])
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

    def testCrapname(self):
        transmog = Transmogrify(self.horiz_img, [('c', '0-510-300-810'),])
        transmog.cropname = "cropped"

        self.assertEqual(transmog.get_processed_filename(),
                         self.cropname_img)


    def testLetterbox(self):
        transmog = Transmogrify(self.square_img, [('l', '300x300-888'), ])
        transmog.save()
        transmog = Transmogrify(self.vert_img, [('l', '300x300-888'), ])
        transmog.save()
        transmog = Transmogrify(self.horiz_img, [('l', '300x300-888'), ])
        transmog.save()

    def testBorder(self):
        transmog = Transmogrify(self.square_img, [('b', '3-f00'), ])
        transmog.save()
        transmog = Transmogrify(self.vert_img, [('b', '3-f00'), ])
        transmog.save()
        transmog = Transmogrify(self.horiz_img, [('b', '3-f00'), ])
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
        utils.PATH_ALIASES = {'/media/': '/testdata/'}
        url = "/media/horiz_img_r200.jpg"
        url += "?%s" % self.doShaHash('_r200')
        result = utils.process_url(url, document_root=HERE)
        self.assertEquals(result['original_file'], get_test_filepath('horiz_img.jpg'))


class TestMakeDirs(TestCase):
    def setUp(self):
        self.test_root = os.path.abspath(
            os.path.join(TESTDATA, "makedirs"))

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


class TestMatchFallback(TestCase):
    def test_match_fallback(self):
        fallback_servers = (
            (r"^media/(.+)", r"\1", "http://example.com/"),
            (r"^static/(.+)", r"static-files/\1", "http://static.example.com/"),
            )

        self.assertEqual(("foo/bar/baz.jpg", "http://example.com/"),
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "media/foo/bar/baz.jpg"))

        self.assertEqual(("static-files/foo/bar/baz.jpg", "http://static.example.com/"),
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "static/foo/bar/baz.jpg"))

        self.assertEqual(None,
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "foo/bar/baz.jpg"))


class TestDoFallback(TestCase):
    def setUp(self):
        self.testdata_root = TESTDATA
        self.fallback_servers = (
            (r"media/(.+)", r"\1", "http://i.usatoday.com/"),
            )

        self.base_path = self.testdata_root

        self.expected_url = \
            "http://i.usatoday.com/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg"

        self.path_info =\
            "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal_r115.jpg"

        self.output_file = os.path.join(self.base_path,
            "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg")

        # clean the slate
        self.tearDown()

    def tearDown(self):
        test_root = os.path.join(self.testdata_root, "media/life")
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
        success = wsgi_handler.do_fallback(self.fallback_servers,
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
        result = wsgi_handler.do_fallback(self.fallback_servers,
                                          self.base_path,
                                          self.path_info)

        # assert that do_fallback did not create the
        # object and the reason was because of the http_error
        self.assertEqual((False, (http_error, (self.expected_url, self.output_file))),
                          result)

        # Ensure the directory tree was not created.
        self.assertTrue(
            not os.path.isdir(os.path.dirname(self.output_file)),
            os.path.dirname(self.output_file))

        # Ensure that the URLopener instance was called with the
        # correct parameters
        instance.retrieve.assert_called_with(self.expected_url)

        # Ensure that the move never happend
        self.assertFalse(mock_move.called)


class TestWSGIHandler(unittest.TestCase):
    def setUp(self):
        self.tearDown()

        settings.BASE_PATH = TESTDATA
        settings.FALLBACK_SERVERS = ((r"dummy", r"", "notused"))
        reload(utils)

    def tearDown(self):
        for filename in ["vert_img_r222.jpg", "vert_img-testcrop.jpg"]:
            absfn = get_test_filepath(filename)

        if os.path.exists(absfn):
            os.remove(absfn)

        reload(settings)

    def doShaHash(self, value):
        import hashlib
        return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

    def test_local(self):
        security_hash = self.doShaHash("_r222")
        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['REQUEST_URI'] = "/vert_img_r222.jpg?" + security_hash

        resp = req.get_response(wsgi_handler.app)
        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img_r222.jpg?" + security_hash,
                         resp.location)
        self.assertTrue(os.path.exists(get_test_filepath("vert_img_r222.jpg")))

    def test_direct_mode(self):
        security_hash = self.doShaHash("_r222")
        qs = urllib.urlencode({"key": security_hash,
                               "path": "/vert_img_r222.jpg"})

        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['QUERY_STRING'] = qs

        resp = req.get_response(wsgi_handler.app)

        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img_r222.jpg?" + security_hash, resp.location)
        self.assertTrue(os.path.exists(get_test_filepath("vert_img_r222.jpg")))

    def test_cropname(self):
        security_hash = self.doShaHash("_r222")
        qs = urllib.urlencode({"key": security_hash,
                               "path": "/vert_img_r222.jpg",
                               "cropname": "testcrop"})

        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['QUERY_STRING'] = qs

        resp = req.get_response(wsgi_handler.app)

        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img-testcrop.jpg?" + security_hash, resp.location)
        self.assertTrue(os.path.exists(get_test_filepath("vert_img-testcrop.jpg")))


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


class TestMatchFallback(TestCase):
    def test_match_fallback(self):
        fallback_servers = (
            (r"^domain/(example.com/.+)", r"", r"http://\1"),
            (r"^media/(.+)", r"\1", "http://example.com/"),
            (r"^static/(.+)", r"static-files/\1", "http://static.example.com/"),
            )

        self.assertEqual("http://example.com/foo/bar/baz.jpg",
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "media/foo/bar/baz.jpg"))

        self.assertEqual("http://static.example.com/static-files/foo/bar/baz.jpg",
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "static/foo/bar/baz.jpg"))


        self.assertEqual("http://example.com/bar/baz.jpg",
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "domain/example.com/bar/baz.jpg"))

        self.assertEqual(None,
                         wsgi_handler.match_fallback(fallback_servers,
                                                     "foo/bar/baz.jpg"))

class TestDoFallback(TestCase):
    def setUp(self):
        self.testdata_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testdata'))
        self.fallback_servers = (
            (r"media/(.+)", r"\1", "http://i.usatoday.com/"),
            )

        self.base_path = self.testdata_root

        self.expected_url = \
            "http://i.usatoday.com/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg"

        self.path_info =\
            "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal_r115.jpg"

        self.output_file = os.path.join(self.base_path,
            "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg")

        # clean the slate
        self.tearDown()

    def tearDown(self):
        test_root = os.path.join(self.testdata_root, "media/life")
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
        success = wsgi_handler.do_fallback(self.fallback_servers,
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
        result = wsgi_handler.do_fallback(self.fallback_servers,
                                          self.base_path,
                                          self.path_info)


        # assert that do_fallback did not create the
        # object and the reason was because of the http_error
        self.assertEqual((False, (http_error, (self.expected_url, self.output_file))),
                          result)

        # Ensure the directory tree was not created.
        self.assertTrue(
            not os.path.isdir(os.path.dirname(self.output_file)),
            os.path.dirname(self.output_file))

        # Ensure that the URLopener instance was called with the
        # correct parameters
        instance.retrieve.assert_called_with(self.expected_url)

        # Ensure that the move never happend
        self.assertFalse(mock_move.called)

class TestWSGIHandler(unittest.TestCase):

    def setUp(self):
        self.tearDown()

        settings.BASE_PATH = os.path.join(HERE, "testdata")
        settings.FALLBACK_SERVERS = ((r"dummy", r"", "notused"))
        reload(utils)

    def tearDown(self):
        for filename in ["vert_img_r222.jpg", "vert_img-testcrop.jpg"]:
            absfn = os.path.join(HERE, "testdata", filename)

        if os.path.exists(absfn):
            os.remove(absfn)

        reload(settings)

    def doShaHash(self, value):
        import hashlib
        return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

    def test_local(self):
        security_hash = self.doShaHash("_r222")
        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['REQUEST_URI'] = "/vert_img_r222.jpg?" + security_hash

        resp = req.get_response(wsgi_handler.app)
        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img_r222.jpg?" + security_hash,
                         resp.location)
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_PATH,
                                                    "vert_img_r222.jpg")))

    def test_direct_mode(self):
        security_hash = self.doShaHash("_r222")
        qs = urllib.urlencode({"key": security_hash,
                               "path": "/vert_img_r222.jpg"})

        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['QUERY_STRING'] = qs

        resp = req.get_response(wsgi_handler.app)

        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img_r222.jpg?" + security_hash , resp.location)
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_PATH,
                                                    "vert_img_r222.jpg")))

    def test_cropname(self):
        security_hash = self.doShaHash("_r222")
        qs = urllib.urlencode({"key": security_hash,
                               "path": "/vert_img_r222.jpg",
                               "cropname": "testcrop"})

        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['QUERY_STRING'] = qs

        resp = req.get_response(wsgi_handler.app)

        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img-testcrop.jpg?" + security_hash , resp.location)
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_PATH,
                                                    "vert_img-testcrop.jpg")))


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
            document_root = TESTDATA
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
