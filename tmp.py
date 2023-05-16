# from src.database.session import db
from src.s3 import s3_image

import sys
import os
import pickle

from datetime import date, timedelta, datetime
import numpy as np
import pandas as pd
import signal
import time
from matplotlib import pyplot as plt

# import colorsys
# from sqlalchemy import func

import boto3

from sqlalchemy import func

import os
import pandas as pd
from shapely.geometry import Polygon
from src.models import *
from src import crud
from src.pingers import *
from src.database.session import db
from src.image_analysis.rekognition.RekognitionImage import *
from src.s3.image import s3_image
import boto3
from tqdm import tqdm
import random
import uuid

# from botocore.exceptions import NoCredentialsError
# import requests
# import mimetypes
# from src.utils import add_two_dicts
# from itertools import product
# from src.crud import image as cr_image
# from src.models import *
# from src.database.session import db
from src.image_analysis.rekognition.utils import *

# from src.s3 import *

# from src.image_analysis.utils import *

if __name__ == "__main__":
    with open(f'{os.getenv("GLOBAL_PATH_TO_REPO")}/data/bernardo.png', "rb") as f:
        image_bytes = bytearray(f.read())
        A = MyRekognitionImage(image_bytes=image_bytes)

    labels = A.get_faces()
    print(labels)
