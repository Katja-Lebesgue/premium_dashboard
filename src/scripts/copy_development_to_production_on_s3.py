import sys

sys.path.append("./.")

from src.s3 import *


def copy_development_to_production_on_s3(
    bucket: str = "creative-features",
    development_path: str = "development/",
    production_path="production/",
    add_global_path: bool = False,
    client=s3_connect(),
):
    delete_from_s3(
        prefix=production_path, bucket=bucket, add_global_path=add_global_path
    )

    copy_on_s3(
        client=client,
        original_prefix=development_path,
        copy_prefix=production_path,
        add_global_path=add_global_path,
    )

    return


def main():
    copy_development_to_production_on_s3()


if __name__ == "__main__":
    main()
