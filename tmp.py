# from src.database.session import db
# from src.s3 import s3_image

import sys
import os
import pickle

from datetime import date, timedelta, datetime
import numpy as np
import pandas as pd
import signal
import time
from matplotlib import pyplot as plt
import colorsys
from sqlalchemy import func

import boto3
from botocore.exceptions import NoCredentialsError
import requests
import mimetypes
from src.utils import add_two_dicts
from itertools import product
from src.crud import image as cr_image
from src.models import *
from src.database.session import db

from src.s3 import *

from src.image_analysis.utils import *

if __name__ == "__main__":
    # s3_image.save_urls_and_performance_to_s3(db=db, force_from_scratch=False)
    # s3_image.filter_and_save_top_n_ads_per_shop_and_month_by_spend()
    # s3_image.initialize_image_df()
    s3_image.save_ad_images_to_s3()
    # shop_id = 20347698
    # df = cr_image.ping_fb_urls_by_shop(
    #     db=db,
    #     shop_id=shop_id,
    # )
