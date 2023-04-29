import json
from io import StringIO

import cv2
import pandas as pd
import numpy as np

from src.utils.s3.utils import s3_client, add_global_s3_folder


def save_csv_to_s3(
    df: pd.DataFrame,
    path: str,
    client=s3_client,
    bucket: str = "creative-features",
    add_global_path: bool = True,
    index: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=index)
    key = path

    client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())

    return


def save_json_to_s3(
    d: dict,
    path: str,
    client=s3_client,
    bucket: str = "creative-features",
    add_global_path: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)

    client.put_object(Bucket=bucket, Key=path, Body=bytes(json.dumps(d).encode("UTF-8")))

    return


def save_image_to_s3(
    img: np.array,
    path: str,
    client=s3_client,
    bucket: str = "creative-features",
    add_global_path: bool = True,
):
    if img is None:
        return

    if add_global_path:
        path = add_global_s3_folder(path)

    success, encoded_img = cv2.imencode(".png", img)
    if success:
        encoded_img = encoded_img.tobytes()
    else:
        raise ValueError("failed to convert image to bytes!")

    client.put_object(Bucket=bucket, Key=path, Body=encoded_img)
