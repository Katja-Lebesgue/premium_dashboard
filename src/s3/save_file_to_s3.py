import sys

sys.path.append("./.")

from src.s3.s3_connect import s3_connect
import pandas as pd
from io import StringIO

import json

from src.utils import *


def save_csv_to_s3(
    df: pd.DataFrame,
    path: str,
    client=s3_connect(),
    bucket: str = "creative-features",
    add_global_path: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    key = path

    client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())

    return


def save_json_to_s3(
    d: dict,
    path: str,
    client=s3_connect(),
    bucket: str = "creative-features",
    add_global_path: bool = True,
):
    if add_global_path:
        path = add_global_s3_folder(path)

    print(path)

    client.put_object(
        Bucket=bucket, Key=path, Body=bytes(json.dumps(d).encode("UTF-8"))
    )

    return
