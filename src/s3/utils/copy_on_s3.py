import sys

sys.path.append("./.")

from src.s3.utils.s3_connect import list_objects_from_prefix, s3_connect


def copy_on_s3(
    original_prefix: str,
    copy_prefix: str,
    add_global_path: bool = False,
    client=s3_connect(),
    bucket: str = "creative-features",
):
    list_of_objects = list_objects_from_prefix(prefix=original_prefix, add_global_folder=add_global_path)

    for key in list_of_objects:
        short_key = key[len(original_prefix) :]
        copy_source = {"Bucket": bucket, "Key": key}
        new_key = copy_prefix + short_key
        print(new_key)
        client.copy(copy_source, bucket, new_key)
