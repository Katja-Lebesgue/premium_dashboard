import json

import cv2
import pandas as pd

from src.utils.s3.utils import s3_client, add_global_s3_folder
from src.utils.pd import read_csv_and_eval


def read_csv_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    evaluate=True,
    add_global_path: bool = True,
):
    if add_global_path:
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
    add_global_path: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)

    object = client.get_object(Bucket=bucket, Key=path)
    file_content = object["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    return json_content


def read_image_from_s3(
    path: str,
    client=s3_client,
    bucket="creative-features",
    add_global_path: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)

    object = client.get_object(Bucket=bucket, Key=path)
    img = np.asarray(bytearray(object["Body"].read()), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    return img
