import os

import boto3
from dotenv import load_dotenv

from src.utils.decorators import print_execution_time

from src.utils.common import add_global_s3_folder

load_dotenv()


def s3_connect():
    boto3.resource(
        service_name="s3",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    return boto3.client("s3")


def s3_resource():
    s3 = boto3.resource(
        service_name="s3",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    return s3


def list_objects_from_prefix(prefix: str, client=s3_connect(), add_global_folder: bool = True):
    if add_global_folder:
        prefix = add_global_s3_folder(prefix)
    client = s3_connect()
    response = client.list_objects_v2(Bucket="creative-features", Prefix=prefix)

    if "Contents" in response.keys():
        list_of_paths = [content["Key"] for content in response["Contents"]]

    else:
        list_of_paths = []

    return list_of_paths
