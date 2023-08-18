import json
import os

import cv2
import pandas as pd
import numpy as np

from src.utils.s3.utils import s3_client, add_global_s3_folder
from src.utils.pd import read_csv_and_eval
from src.utils.image.my_image import MyImage


def read_csv_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    evaluate=True,
    add_global_folder: bool = True,
):
    if add_global_folder:
        path = add_global_s3_folder(path)

    object = client.get_object(Bucket=bucket, Key=path)

    if evaluate:
        df = read_csv_and_eval(object["Body"])
    else:
        df = pd.read_csv(object["Body"])

    return df


def read_json_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    add_global_folder: bool = True,
):
    if add_global_folder:
        path = add_global_s3_folder(path)

    object = client.get_object(Bucket=bucket, Key=path)
    file_content = object["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    return json_content


def read_image_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    add_global_folder: bool = True,
):
    image_bytes = read_image_bytes_from_s3(
        path=path, client=client, bucket=bucket, add_global_folder=add_global_folder
    )

    file_name, _ = os.path.splitext(os.path.basename(path))

    return MyImage(image_bytes=image_bytes, name=file_name)


def read_image_bytes_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    add_global_folder: bool = True,
):
    if add_global_folder:
        path = add_global_s3_folder(path)
    object = client.get_object(Bucket=bucket, Key=path)
    image_bytes = bytearray(object["Body"].read())
    return image_bytes
