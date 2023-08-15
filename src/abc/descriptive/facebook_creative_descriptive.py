from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.abc.descriptive.descriptive import Descriptive
from src.pingers import ping_facebook_creative_and_performance


class FacebookCreativeDescriptive(Descriptive):
    descriptive_columns = BOOLEAN_TEXT_FEATURES
    tag = "facebook_creative"
