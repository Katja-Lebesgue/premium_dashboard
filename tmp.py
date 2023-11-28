from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from enum import Enum
from src.services import FacebookCreativeDescriptive
from src.services import facebook_creative_descriptive_saver as fcd
from src.services import facebook_target_descriptive_saver as ftd
from src.database.session import SessionLocal
from src.pingers import *
from src.utils import *
from src import crud
from src.interfaces.descriptive import DescriptiveDF
from src.crud.utils.get_performance import get_performance, get_conversion_rates_dict

db = SessionLocal()
end_date_plus_one = date(year=2023, month=8, day=1)
end_date = end_date_plus_one - timedelta(days=1)
start_date = end_date_plus_one - relativedelta(months=24)
shop_id = 2445081
df = fcd.get_shop_descriptive_df(db=db, shop_id=16038)
