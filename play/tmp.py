import sys
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

sys.path.append(".")

from src.pingers import *
from src.database.session import db

ping_ads_insights_all_platforms(db=db)
