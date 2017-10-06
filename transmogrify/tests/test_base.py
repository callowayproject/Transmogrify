import unittest
import os
# import urllib
# import shutil

# import wsgi_handler
from transmogrify import wsgi as wsgi_handler
from transmogrify.core import Transmogrify
from transmogrify import processors, utils, settings

from webob import Request
import mock
from PIL import Image

HERE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TESTDATA = os.path.abspath(settings.ORIG_BASE_PATH)
os.environ['TRANSMOGRIFY_SECRET'] = 'secret'


def get_test_filepath(filename):
    """
    return a full filepath to the test data directory
    """
    return os.path.abspath(os.path.join(settings.ORIG_BASE_PATH, filename))


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
            ("foo_", []),
            utils.parse_action_tuples("foo_")
        )

        self.assertEqual(
            ("foo_bar", [("r", "100")]),
            utils.parse_action_tuples("foo_bar_r100")
        )

        self.assertEqual(
            ("", [("c", "1088")]),
            utils.parse_action_tuples("c1088")
        )

        self.assertEqual(
            ("c1088-1_1", []),
            utils.parse_action_tuples("c1088-1_1")
        )

        self.assertEqual(
            ("", [("c", "1088"), ("c", "0-0-100-100")]),
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
        self.square_img = 'square_img.jpg'
        self.vert_img = 'vert_img.jpg'
        self.horiz_img = 'horiz_img.jpg'
        self.cropname_img = 'horiz_img-cropped.jpg'
        self.animated = 'animated.gif'

    def test_thumbnail(self):
        expected_square = (300, 300)
        expected_vert = (168, 300)
        expected_horiz = (300, 208)
        # expected_animated = (300, 214)
        transmog = Transmogrify(utils.generate_url(self.square_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)
        # transmog = Transmogrify(utils.generate_url(self.animated, '_r300x300'), "")
        # transmog.save()
        # img = Image.open(transmog.get_processed_filename())
        # self.assertEqual(expected_animated, img.size)

    def test_resize(self):
        expected_square = (300, 300)
        expected_vert = (168, 300)
        expected_horiz = (300, 208)
        # expected_animated = (300, 214)
        transmog = Transmogrify(utils.generate_url(self.square_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_vert, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_r300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_horiz, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_r300x300'), "")
        # transmog.save()
        # img = Image.open(transmog.get_processed_filename())
        # self.assertEqual(expected_animated, img.size)

    def test_force_fit(self):
        expected_square = (300, 300)
        transmog = Transmogrify(utils.generate_url(self.square_img, '_s300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_s300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_s300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_s300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

    def test_crop(self):
        expected_square = (300, 300)
        transmog = Transmogrify(utils.generate_url(self.square_img, '_c300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_c300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_c300x300'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)
        # transmog = Transmogrify(utils.generate_url(self.animated, '_c300x300'), "")
        # transmog.save()
        # img = Image.open(transmog.get_processed_filename())
        # self.assertEqual(expected_square, img.size)

    def test_crop_bbox(self):
        expected_square = (300, 300)
        transmog = Transmogrify(utils.generate_url(self.square_img, '_c100-100-400-400'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        transmog = Transmogrify(utils.generate_url(self.vert_img, '_c0-100-300-400'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_c0-410-300-710'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        # 810 is larger than the image, PIL adds black to the extra space.
        # who knows if this is desirable but at least it doesn't raise
        # an exception.
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_c0-510-300-810'), "")
        transmog.save()
        img = Image.open(transmog.get_processed_filename())
        self.assertEqual(expected_square, img.size)

        # transmog = Transmogrify(utils.generate_url(self.animated, '_c0-410-300-710'))
        # transmog.save()
        # img = Image.open(transmog.get_processed_filename())
        # self.assertEqual(expected_square, img.size)

    def test_cropname(self):
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_c0-510-300-810'))
        transmog.cropname = "cropped"
        _, proc_name = os.path.split(transmog.get_processed_filename())

        self.assertEqual(proc_name, self.cropname_img)

    def test_letterbox(self):
        transmog = Transmogrify(utils.generate_url(self.square_img, '_l300x300-888'))
        transmog.save()
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_l300x300-888'))
        transmog.save()
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_l300x300-888'))
        transmog.save()
        # transmog = Transmogrify(utils.generate_url(self.animated, '_l300x300-888'))
        # transmog.save()

    def test_border(self):
        transmog = Transmogrify(utils.generate_url(self.square_img, '_b3-f00'))
        transmog.save()
        transmog = Transmogrify(utils.generate_url(self.vert_img, '_b3-f00'))
        transmog.save()
        transmog = Transmogrify(utils.generate_url(self.horiz_img, '_b3-f00'))
        transmog.save()

        security_hash = utils.generate_url(self.horiz_img, '_b3-f00').split('?')[1]
        self.assertEqual(security_hash, transmog.get_security_hash())
        # transmog = Transmogrify(self.animated, [('b', '3-f00'), ])
        # transmog.save()


class UrlProcessingTest(unittest.TestCase):
    """
    Test aspects of URL processing.
    """
    def do_sha_hash(self, value):
        import hashlib
        return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

    def test_aliases(self):
        assert '^/assets/' in settings.PATH_ALIASES
        url = "/assets/horiz_img_r200.jpg"
        url += "?%s" % self.do_sha_hash('_r200')
        result = utils.process_url(url, document_root=TESTDATA)
        self.assertEquals(result['original_file'], get_test_filepath('horiz_img.jpg'))

    def test_no_hash(self):
        from transmogrify.network import Http404

        self.assertRaises(Http404, utils.process_url, '/horiz_img_r200.jpg', document_root=TESTDATA)

    def test_external_url(self):
        result = utils.process_url('/external/http://example.com/foo.jpg', document_root=TESTDATA)

        self.assertTrue(result['is_external'])
        self.assertEquals(result['external_url'], 'http://example.com/foo.jpg')

    def test_bad_prefix(self):
        from transmogrify.network import Http404

        self.assertRaises(Http404, utils.process_url, '../../horiz_img_r200.jpg', document_root=TESTDATA)

    def test_missing_original(self):
        from transmogrify.network import Http404

        self.assertRaises(Http404, utils.process_url, '/horiz_image_r200.jpg', document_root=TESTDATA)

# class TestMakeDirs(unittest.TestCase):
#     def setUp(self):
#         self.test_root = os.path.abspath(
#             get_test_filepath("makedirs"))

#     def tearDown(self):
#         dirs = [
#             os.path.join(self.test_root, "didnotexist"),
#             os.path.join(self.test_root, "partiallyexists", "foo", "bar"),
#         ]

#         for item in dirs:
#             if os.path.exists(item):
#                 shutil.rmtree(item)

#     def test_didnotexist(self):
#         path = os.path.join(self.test_root,
#                             "didnotexist", "foo", "bar", "baz")
#         wsgi_handler.makedirs(path)
#         self.assertTrue(os.path.isdir(path))

#     def test_exists(self):
#         path = os.path.join(self.test_root,
#                             "exists", "foo", "bar", "baz")
#         wsgi_handler.makedirs(path)
#         self.assertTrue(os.path.isdir(path))

#     def test_partiallyexists(self):
#         path = os.path.join(self.test_root,
#                             "partiallyexists", "foo", "bar", "baz")
#         wsgi_handler.makedirs(path)
#         self.assertTrue(os.path.isdir(path))

#     def test_nondirbit(self):
#         path = os.path.join(self.test_root,
#                             "nondirbit", "foo", "bar", "baz")

#         self.assertRaises(OSError, wsgi_handler.makedirs, path)


# class TestMatchFallback(TestCase):
#     def test_match_fallback(self):
#         fallback_servers = (
#             (r"^domain/(example.com/.+)", r"", r"http://\1"),
#             (r"^media/(.+)", r"\1", "http://example.com/"),
#             (r"^static/(.+)", r"static-files/\1", "http://static.example.com/"),
#         )

#         self.assertEqual("http://example.com/foo/bar/baz.jpg",
#                          wsgi_handler.match_fallback(fallback_servers,
#                                                      "media/foo/bar/baz.jpg"))

#         self.assertEqual("http://static.example.com/static-files/foo/bar/baz.jpg",
#                          wsgi_handler.match_fallback(fallback_servers,
#                                                      "static/foo/bar/baz.jpg"))

#         self.assertEqual("http://example.com/bar/baz.jpg",
#                          wsgi_handler.match_fallback(fallback_servers,
#                                                      "domain/example.com/bar/baz.jpg"))

#         self.assertEqual(None,
#                          wsgi_handler.match_fallback(fallback_servers,
#                                                      "foo/bar/baz.jpg"))


# class TestDoFallback(TestCase):
#     def setUp(self):
#         self.testdata_root = TESTDATA
#         self.fallback_servers = (
#             (r"media/(.+)", r"\1", "http://i.usatoday.com/"),
#         )

#         self.base_path = self.testdata_root

#         self.expected_url = \
#             "http://i.usatoday.com/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg"

#         self.path_info =\
#             "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal_r115.jpg"

#         self.output_file = os.path.join(self.base_path,
#             "media/life/gallery/2012/l120523_untamed/02untamed-pg-horizontal.jpg")

#         # clean the slate
#         self.tearDown()

#     def tearDown(self):
#         test_root = os.path.join(self.testdata_root, "media/life")
#         if os.path.exists(test_root):
#             shutil.rmtree(test_root)

#     @mock.patch("shutil.move")
#     @mock.patch("os.path.exists")
#     @mock.patch("urllib.URLopener")
#     def test_200(self, mock_opener, mock_exists, mock_move):
#         ##
#         # Setup mocks
#         ##
#         instance = mock_opener.return_value
#         instance.retrieve.return_value = ("/tmp/sometmpfilename", mock.Mock())

#         mock_exists.return_value = False

#         ##
#         # Execute
#         ##
#         success = wsgi_handler.do_fallback(self.fallback_servers,
#                                            self.base_path,
#                                            self.path_info)

#         ##
#         # Test
#         ##

#         self.assertTrue(success)

#         # Ensure that the URLopener instance was called with the
#         # correct parameters
#         instance.retrieve.assert_called_with(self.expected_url)

#         # Ensure the directory tree was created.
#         self.assertTrue(os.path.isdir(os.path.dirname(self.output_file)))

#         # Ensure that shutil.move was called correctly
#         mock_move.assert_called_with("/tmp/sometmpfilename",
#                                      self.output_file)

#     @mock.patch("shutil.move")
#     @mock.patch("os.path.exists")
#     @mock.patch("urllib.URLopener")
#     def test_non200(self, mock_opener, mock_exists, mock_move):
#         ##
#         # Setup mocks
#         ##
#         instance = mock_opener.return_value
#         http_error = IOError('http error', 404, 'NOT FOUND', mock.Mock())
#         instance.retrieve.side_effect = http_error
#         mock_exists.return_value = False

#         ##
#         # Execute
#         ##
#         result = wsgi_handler.do_fallback(self.fallback_servers,
#                                           self.base_path,
#                                           self.path_info)

#         # assert that do_fallback did not create the
#         # object and the reason was because of the http_error
#         self.assertEqual((False, (http_error, (self.expected_url, self.output_file))),
#                           result)

#         # Ensure the directory tree was not created.
#         self.assertTrue(
#             not os.path.isdir(os.path.dirname(self.output_file)),
#             os.path.dirname(self.output_file))

#         # Ensure that the URLopener instance was called with the
#         # correct parameters
#         instance.retrieve.assert_called_with(self.expected_url)

#         # Ensure that the move never happend
#         self.assertFalse(mock_move.called)


class TestWSGIHandler(unittest.TestCase):
    def setUp(self):
        self.tearDown()

        settings.BASE_PATH = TESTDATA
        settings.FALLBACK_SERVERS = ((r"dummy", r"", "notused"))
        reload(utils)

    def tearDown(self):
        for filename in ["vert_img_r222.jpg", "vert_img-testcrop.jpg", ]:
            absfn = get_test_filepath(filename)

        if os.path.exists(absfn):
            os.remove(absfn)

        reload(settings)

    def do_sha_hash(self, value):
        import hashlib
        return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

    def test_local(self):
        security_hash = self.do_sha_hash("_r222")
        req = Request.blank("/")
        req.environ['SERVER_NAME'] = 'testserver'
        req.environ['REQUEST_URI'] = "/vert_img_r222.jpg?" + security_hash

        resp = req.get_response(wsgi_handler.app)
        self.assertEqual("", resp.body)
        self.assertEqual("302 Found", resp.status)
        self.assertEqual("/vert_img_r222.jpg?" + security_hash,
                         resp.location)
        self.assertTrue(os.path.exists(get_test_filepath("vert_img_r222.jpg")))

    # def test_direct_mode(self):
    #     security_hash = self.do_sha_hash("_r222")
    #     qs = urllib.urlencode({"key": security_hash,
    #                            "path": "/vert_img_r222.jpg"})

    #     req = Request.blank("/")
    #     req.environ['TRANSMOGRIFY_ORIG_BASE_PATH'] = TESTDATA
    #     req.environ['SERVER_NAME'] = 'testserver'
    #     req.environ['QUERY_STRING'] = qs
    #     req.environ['TRANSMOGRIFY_DEBUG'] = 'True'

    #     resp = req.get_response(wsgi_handler.app)

    #     self.assertEqual("", resp.body)
    #     self.assertEqual("302 Found", resp.status)
    #     self.assertEqual("/vert_img_r222.jpg?" + security_hash, resp.location)
    #     self.assertTrue(os.path.exists(get_test_filepath("vert_img_r222.jpg")))

    # def test_original(self):
    #     qs = urllib.urlencode({"path": "/vert_img.jpg"})

    #     req = Request.blank("/")

    #     req.environ['TRANSMOGRIFY_ORIG_BASE_PATH'] = TESTDATA
    #     req.environ['SERVER_NAME'] = 'testserver'
    #     req.environ['QUERY_STRING'] = qs
    #     req.environ['TRANSMOGRIFY_DEBUG'] = 'True'

    #     resp = req.get_response(wsgi_handler.app)

    #     self.assertEqual("", resp.body)
    #     self.assertEqual("302 Found", resp.status)
    #     self.assertEqual("/vert_img.jpg", resp.location)
    #     self.assertTrue(os.path.exists(get_test_filepath("vert_img.jpg")))

    # def test_cropname(self):
    #     security_hash = self.do_sha_hash("_r222")
    #     qs = urllib.urlencode({"key": security_hash,
    #                            "path": "/vert_img_r222.jpg",
    #                            "cropname": "testcrop"})

    #     req = Request.blank("/")
    #     req.environ['TRANSMOGRIFY_ORIG_BASE_PATH'] = TESTDATA
    #     req.environ['SERVER_NAME'] = 'testserver'
    #     req.environ['QUERY_STRING'] = qs

    #     resp = req.get_response(wsgi_handler.app)

    #     self.assertEqual("", resp.body)
    #     self.assertEqual("302 Found", resp.status)
    #     print resp.location
    #     self.assertEqual("/vert_img-testcrop.jpg?" + security_hash, resp.location)
    #     self.assertTrue(os.path.exists(get_test_filepath("vert_img-testcrop.jpg")))


# class TestOptimize(unittest.TestCase):
#     def setUp(self):
#         from PIL import Image

#         self.square_img = Image.open(get_test_filepath('square_img.jpg'))
#         self.vert_img = Image.open(get_test_filepath('vert_img.jpg'))
#         self.horiz_img = Image.open(get_test_filepath('horiz_img.jpg'))
#         self.cropname_img = Image.open(get_test_filepath('horiz_img-cropped.jpg'))
#         self.animated = Image.open(get_test_filepath('animated.gif'))

#     def test_has_optimize_cmd(self):
#         from transmogrify.utils import is_tool

#         self.assertTrue(is_tool('imagemin'))

#     def test_optimize(self):
#         import os
#         from transmogrify import optimize
#         # from PIL import Image
#         os.environ['IMAGE_OPTIMIZATION_CMD'] = 'imagemin'
#         optimized_square = optimize.optimize(self.square_img, 'jpeg')
#         # optimized_animated = optimize.optimize(self.animated)
#         optim_square_filepath = get_test_filepath('square_img.optim.jpg')
#         # optim_animated_filepath = get_test_filepath('animated.optim.gif')
#         optimized_square.save(optim_square_filepath, 'jpeg', 80)


# class TemplateTagTest(TestCase):
#     def do_sha_hash(self, value):
#         import hashlib
#         return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

#     def test_resize(self):
#         t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_r300.jpg?%s' % self.do_sha_hash("_r300"))
#         t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg x300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_rx300.jpg?%s' % self.do_sha_hash("_rx300"))
#         t = Template("{% load transmogrifiers %}{% resize /test/picture.jpg 300x300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_r300x300.jpg?%s' % self.do_sha_hash("_r300x300"))

#     def test_forcefit(self):
#         t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_s300.jpg?%s' % self.do_sha_hash("_s300"))
#         t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg x300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_sx300.jpg?%s' % self.do_sha_hash("_sx300"))
#         t = Template("{% load transmogrifiers %}{% forcefit /test/picture.jpg 300x300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_s300x300.jpg?%s' % self.do_sha_hash("_s300x300"))

#     def test_crop(self):
#         t = Template("{% load transmogrifiers %}{% crop /test/picture.jpg 300x300 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_c300x300.jpg?%s' % self.do_sha_hash("_c300x300"))

#     def test_crop_bbox(self):
#         t = Template("{% load transmogrifiers %}{% crop /test/picture.jpg 0-0-100-100 %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_c0-0-100-100.jpg?%s' % self.do_sha_hash("_c0-0-100-100"))

#     def test_letterbox(self):
#         t = Template("{% load transmogrifiers %}{% letterbox /test/picture.jpg 300x300 #f8129b  %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_l300x300-f8129b.jpg?%s' % self.do_sha_hash("_l300x300-f8129b"))

#     def test_border(self):
#         t = Template("{% load transmogrifiers %}{% border /test/picture.jpg 1 #f8129b %}")
#         self.assertEqual(t.render(Context({})), '/test/picture_b1-f8129b.jpg?%s' % self.do_sha_hash("_b1-f8129b"))

#     def test_existing_action_string(self):
#         t = Template("{% load transmogrifiers %}{% resize /test/picture_c0-0-300-300.jpg 300x300 %}")
#         self.assertEqual(t.render(Context({})), u'/test/picture_c0-0-300-300_r300x300.jpg?%s' % self.do_sha_hash("_c0-0-300-300_r300x300"))

#     def test_mask(self):
#         t = Template("{% load transmogrifiers %}{% mask /test/picture.jpg %}")
#         self.assertEqual(t.render(Context({})), u'/test/picture_m.jpg?%s' % self.do_sha_hash("_m"))


# class TemplateFilterTest(TestCase):
#     def do_sha_hash(self, value):
#         import hashlib
#         return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

#     def test_resize(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|resize:"300" }}')
#         self.assertEqual(t.render(context), '/test/picture_r300.jpg?%s' % self.do_sha_hash("_r300"))
#         t = Template('{% load transmogrifiers %}{{ img_url|resize:"x300" }}')
#         self.assertEqual(t.render(context), '/test/picture_rx300.jpg?%s' % self.do_sha_hash("_rx300"))
#         t = Template('{% load transmogrifiers %}{{ img_url|resize:"300x300" }}')
#         self.assertEqual(t.render(context), '/test/picture_r300x300.jpg?%s' % self.do_sha_hash("_r300x300"))

#     def test_force_fit(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"300" }}')
#         self.assertEqual(t.render(context), '/test/picture_s300.jpg?%s' % self.do_sha_hash("_s300"))
#         t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"x300" }}')
#         self.assertEqual(t.render(context), '/test/picture_sx300.jpg?%s' % self.do_sha_hash("_sx300"))
#         t = Template('{% load transmogrifiers %}{{ img_url|forcefit:"300x300" }}')
#         self.assertEqual(t.render(context), '/test/picture_s300x300.jpg?%s' % self.do_sha_hash("_s300x300"))

#     def test_crop(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|crop:"300x300" }}')
#         self.assertEqual(t.render(context), '/test/picture_c300x300.jpg?%s' % self.do_sha_hash("_c300x300"))

#     def test_crop_bbox(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|crop:"0-0-100-100" }}')
#         self.assertEqual(t.render(context), '/test/picture_c0-0-100-100.jpg?%s' % self.do_sha_hash("_c0-0-100-100"))

#     def test_letterbox(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|letterbox:"300x300 #f8129b" }}')
#         self.assertEqual(t.render(context), '/test/picture_l300x300-f8129b.jpg?%s' % self.do_sha_hash("_l300x300-f8129b"))

#     def test_border(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|border:"1 #f8129b" }}')
#         self.assertEqual(t.render(context), '/test/picture_b1-f8129b.jpg?%s' % self.do_sha_hash("_b1-f8129b"))

#     def test_mask(self):
#         context = Context({"img_url": "/test/picture.jpg"})

#         t = Template('{% load transmogrifiers %}{{ img_url|mask }}')
#         self.assertEqual(t.render(context), '/test/picture_m.jpg?%s' % self.do_sha_hash("_m"))

#     def test_chaining(self):
#         context = Context({"img_url": "/test/picture.jpg"})
#         t = Template('{% load transmogrifiers %}{{ img_url|crop:"0-0-300-300"|resize:"x100" }}')
#         self.assertEqual(t.render(context), '/test/picture_c0-0-300-300_rx100.jpg?%s' % self.do_sha_hash("_c0-0-300-300_rx100"))

#     def test_existing_action_string(self):
#         context = Context({"img_url": "/test/picture_c0-0-300-300.jpg"})
#         t = Template('{% load transmogrifiers %}{{ img_url|resize:"x100" }}')
#         self.assertEqual(t.render(context), '/test/picture_c0-0-300-300_rx100.jpg?%s' % self.do_sha_hash("_c0-0-300-300_rx100"))


# class ViewTest(TestCase):
#     def do_sha_hash(self, value):
#         import hashlib
#         return hashlib.sha1(value + settings.SECRET_KEY).hexdigest()

#     def test_view(self):
#         rf = RequestFactory()
#         path = '/horiz_img_r300x400.jpg'
#         document_root = TESTDATA
#         request = rf.get('%s?%s' % (path, self.do_sha_hash("_r300x400")))
#         import views
#         response = views.transmogrify_serve(request, path, document_root)
#         self.assertEqual(response.status_code, 200)


class TestUtil(unittest.TestCase):
    def test_generate_url(self):
        self.assertEqual(settings.SECRET_KEY, 'secret')
        expected = ("http://example.com/media/foo_r200.jpg"
                    "?d657deac24715ccdd7a3df65f4ea3f9be5bb6454")
        result = utils.generate_url("http://example.com/media/foo.jpg",
                                    "_r200")
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
