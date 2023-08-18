from loguru import logger
from src.utils.s3.utils import s3_resource, add_global_s3_folder


def delete_from_s3(
    prefix: str,
    s3_resource=s3_resource,
    bucket: str = "creative-features",
    add_global_folder: bool = False,
):
    if add_global_folder:
        prefix = add_global_s3_folder(prefix)

    bucket = s3_resource.Bucket(bucket)
    objects = bucket.objects.filter(Prefix=prefix)
    objects.delete()
