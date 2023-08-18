import os

import boto3
from dotenv import load_dotenv
from enum import Enum
from loguru import logger

load_dotenv()


class s3ConnectionType(str, Enum):
    resource = "resource"
    client = "client"


def s3_connect(conn_type: s3ConnectionType = s3ConnectionType.client):
    resource = boto3.resource(
        service_name="s3",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    if conn_type == s3ConnectionType.resource:
        return resource
    else:
        return boto3.client("s3")


def add_global_s3_folder(path):
    return f"{os.getenv('S3_PATH')}/{path}"


s3_client = s3_connect()
s3_resource = s3_connect(conn_type=s3ConnectionType.resource)


def list_objects_from_prefix(prefix: str, client=s3_client, add_global_folder: bool = True):
    if add_global_folder:
        prefix = add_global_s3_folder(prefix)
    response = client.list_objects_v2(Bucket="creative-features", Prefix=prefix)

    if "Contents" in response.keys():
        list_of_paths = [content["Key"] for content in response["Contents"]]

    else:
        list_of_paths = []

    return list_of_paths
