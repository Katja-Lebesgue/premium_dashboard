from src.utils.s3.utils import s3_resource, add_global_s3_folder


def delete_from_s3(
    prefix: str,
    s3=s3_resource,
    bucket: str = "creative-features",
    add_global_path: bool = False,
):
    if add_global_path:
        prefix = add_global_s3_folder(prefix)

    bucket = s3.Bucket(bucket)
    bucket.objects.filter(Prefix=prefix).delete()
