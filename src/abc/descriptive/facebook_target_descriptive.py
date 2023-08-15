from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.abc.descriptive.descriptive import Descriptive
from src.pingers import ping_target_and_performance


class FacebookTargetDescriptive(Descriptive):
    descriptive_columns = ["target", "gender", "audience"]
    tag = "facebook_target"
