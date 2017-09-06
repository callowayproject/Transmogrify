import logging
import boto3
import daiquiri

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def _parse_s3_file(original_file):
    """
    Convert `s3://bucketname/path/to/file.txt` to ('bucketname', 'path/to/file.txt')
    """
    bits = original_file.replace('s3://', '').split("/")
    bucket = bits[0]
    object_key = "/".join(bits[1:])
    return bucket, object_key


def file_exists(original_file):
    """
    Validate the original file is in the S3 bucket
    """
    s3 = boto3.resource('s3')
    bucket_name, object_key = _parse_s3_file(original_file)
    bucket = s3.Bucket(bucket_name)
    bucket_iterator = bucket.objects.filter(Prefix=object_key)
    bucket_list = [x for x in bucket_iterator]
    logger.debug("Bucket List: {0}".format(", ".join([x.key for x in bucket_list])))
    logger.debug("bucket_list length: {0}".format(len(bucket_list)))
    return len(bucket_list) == 1
    # if len(bucket_list) != 1:
    #     # If the path is a directory, S3 doesn't return anything
    #     logger.debug("bucket_list is not equal to 1 ({0})".format(len(bucket_list)))
    #     return False
    # return True


def callback(bytes):
    print bytes


def get_file(original_file):
    """
    original file should be s3://bucketname/path/to/file.txt

    returns a Buffer with the file in it
    """
    import cStringIO
    import boto3
    s3 = boto3.resource('s3')
    bucket_name, object_key = _parse_s3_file(original_file)
    logger.debug("Downloading {0} from {1}".format(object_key, bucket_name))
    bucket = s3.Bucket(bucket_name)
    output = cStringIO.StringIO()
    bucket.download_fileobj(object_key, output)
    output.reset()
    return output


def put_file(buffer, modified_file):
    """
    write the buffer to modified_file.

    modified_file should be in the format 's3://bucketname/path/to/file.txt'
    """
    import mimetypes
    import boto3
    file_type, _ = mimetypes.guess_type(modified_file)

    s3 = boto3.resource('s3')
    bucket_name, object_key = _parse_s3_file(modified_file)
    extra_args = {
        'ACL': 'public-read',
        'ContentType': file_type
    }
    bucket = s3.Bucket(bucket_name)
    logger.info("Uploading {0} to {1}".format(object_key, bucket_name))
    bucket.upload_fileobj(buffer, object_key, ExtraArgs=extra_args)
