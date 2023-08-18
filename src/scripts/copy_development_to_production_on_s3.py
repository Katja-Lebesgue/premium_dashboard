import sys

sys.path.append("./.")

from src.utils.s3 import *


def copy_development_to_production_on_s3(
    bucket: str = os.getenv("S3_BUCKET"),
    prod_path: str = os.getenv("S3_PROD_PATH"),
    dev_path: str = os.getenv("S3_DEV_PATH"),
):
    delete_from_s3(prefix=prod_path, bucket=bucket, add_global_folder=False)

    copy_on_s3(
        original_prefix=dev_path,
        target_prefix=prod_path,
        add_global_folder=False,
    )


if __name__ == "__main__":
    copy_development_to_production_on_s3()
