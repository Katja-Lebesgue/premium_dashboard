from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.abc.descriptive.descriptive import Descriptive
from src import crud


class GoogleCampaignTypeDescriptive(Descriptive):
    descriptive_columns = ["campaign_type"]
    tag = "google_campaign_type"
