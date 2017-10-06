"""
Test the utils
"""
from transmogrify import utils


def test_is_tool():
    assert utils.is_tool('date') is True
    assert utils.is_tool('foo') is False


def test_purge_security_hash():
    from hashlib import sha1
    from transmogrify.settings import SECRET_KEY

    security_hash = sha1('PURGE' + SECRET_KEY).hexdigest()
    assert utils.is_valid_security('PURGE', security_hash) is True


def test_get_cached_files():
    import os
    from transmogrify import settings
    from transmogrify.core import Transmogrify
    testdata = os.path.abspath(settings.BASE_PATH)
    t = Transmogrify('/horiz_img_r300x300.jpg?debug')
    t.save()
    result = utils.get_cached_files('/horiz_img.jpg', document_root=testdata)
    filenames = [x.replace(testdata, '') for x in result]
    assert '/horiz_img_r300x300.jpg' in filenames


def test_settings_stuff():
    from transmogrify import settings

    assert settings.bool_from_env('FOO', False) is False
    assert settings.bool_from_env('FOO', 'False') is False
    assert settings.bool_from_env('FOO', 'false') is False
    assert settings.bool_from_env('FOO', 'F') is False
    assert settings.bool_from_env('FOO', 'f') is False
    assert settings.bool_from_env('FOO', '0') is False
    assert settings.bool_from_env('FOO', 'True')
    assert settings.bool_from_env('FOO', 'true')
    assert settings.bool_from_env('FOO', 'T')
    assert settings.bool_from_env('FOO', 't')
    assert settings.bool_from_env('FOO', '1')
    assert settings.list_from_env("FOO", '1,2,3,4') == ['1', '2', '3', '4']
    assert settings.lists_from_env("FOO", '1,2:3,4') == [['1', '2'], ['3', '4']]
