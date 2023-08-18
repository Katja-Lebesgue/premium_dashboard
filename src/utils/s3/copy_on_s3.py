import os
from loguru import logger
from src.utils.s3.utils import s3_resource, list_objects_from_prefix
from src.utils.common import print_dict
import botocore


def copy_on_s3(
    original_prefix: str,
    target_prefix: str,
    add_global_folder: bool = False,
    s3_resource=s3_resource,
    bucket: str = os.getenv("S3_BUCKET"),
):
    if add_global_folder:
        original_prefix = add_global_folder(original_prefix)
        target_prefix = add_global_folder(target_prefix)

    s3_bucket = s3_resource.Bucket(bucket)
    logger.debug(f"{original_prefix = }")
    objects = s3_bucket.objects.filter(Prefix=original_prefix)
    try:
        for obj in objects:
            pass
            # old_source = {"Bucket": bucket, "Key": obj.key}
            # # replace the prefix
            # new_key = obj.key.replace(original_prefix, target_prefix, 1)
            # new_obj = s3_bucket.Object(new_key)
            # new_obj.copy(old_source)
    except botocore.exceptions.ClientError as err:
        print_dict(err.response)
