import os
from loguru import logger
from src.utils.s3.utils import s3_client, list_objects_from_prefix
from src.utils.common import print_dict
import botocore


def copy_on_s3(
    original_prefix: str,
    target_prefix: str,
    add_global_folder: bool = False,
    s3_client=s3_client,
    bucket: str = os.getenv("S3_BUCKET"),
):
    if add_global_folder:
        original_prefix = add_global_folder(original_prefix)
        target_prefix = add_global_folder(target_prefix)

    object_paths = list_objects_from_prefix(prefix=original_prefix, add_global_folder=False)
    for obj_path in object_paths:
        copy_source = {
            "Bucket": bucket,
            "Key": obj_path,
        }
        new_path = os.path.join(target_prefix, obj_path.removeprefix(original_prefix).removeprefix("/"))
        s3_client.copy(copy_source, bucket, new_path)
