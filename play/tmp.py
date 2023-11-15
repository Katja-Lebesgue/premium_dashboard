import sys
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

sys.path.append(".")

import webbrowser
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from numbers import Number

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, not_, or_

from src import crud
from src.abc.descriptive import DescriptiveDF
from src.crud.utils.get_performance import get_conversion_rates_dict
from src.database.session import SessionLocal
from src.models import *
from src.models.enums.facebook import Target
from src.models.enums.facebook.creative_features import BOOLEAN_TEXT_FEATURES
from src.pingers import *
from src.utils import *

db = SessionLocal()
end_date_plus_one = date(year=2023, month=8, day=1)
end_date = end_date_plus_one - timedelta(days=1)
start_date = end_date_plus_one - relativedelta(months=12)
shop_id = 44301396

df = ping_facebook_creative_target_and_performance(db=db, shop_id=16038, start_date="2023-09-20")
