import sys

sys.path.append("./.")

import pandas as pd
import json

import os
from dotenv import load_dotenv

load_dotenv()

from src.s3.s3_connect import s3_connect
from src.utils.common import read_csv_and_eval

from src.utils import *


def read_csv_from_s3(
    path: str,
    client=s3_connect(),
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
    client=s3_connect(),
    bucket="creative-features",
    add_global_path: bool = True,
):

    if add_global_path:
        path = add_global_s3_folder(path)

    object = client.get_object(Bucket=bucket, Key=path)
    file_content = object["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    return json_content
