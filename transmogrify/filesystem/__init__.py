"""
Slight abstraction of the filesystem calls to allow for other types of storage
"""
import os


def makedirs(dirname):
    if dirname.startswith("s3://"):
        # S3 will make the directories when we submit the file
        return
    else:
        assert dirname.startswith("/"), "dirname must be absolute"

    bits = dirname.split(os.sep)[1:]

    root = "/"

    for bit in bits:
        root = os.path.join(root, bit)

        if not os.path.lexists(root):
            os.mkdir(root)
        elif not os.path.isdir(root):
            raise OSError("%s is exists, but is not a directory." % (root, ))
        else:  # exists and is a dir
            pass


def file_exists(original_file):
    """
    Check to make sure the original file exists
    """
    if original_file.startswith("s3://"):
        from filesystem import s3
        return s3.file_exists(original_file)
    else:
        if not os.path.exists(original_file):
            return False
        if not os.path.isfile(original_file):
            return False
    return True
