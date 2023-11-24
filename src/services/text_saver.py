from datetime import date
from src.abc import S3ReaderWriter
from src.pingers import ping_facebook_creative_target_and_performance
from src.utils import *
from src import crud

from sqlalchemy.orm import Session
import pandas as pd


class TextDF(str, Enum):
    month = "month"
    samples_by_industry = "samples_by_industry"
    length = "length"
    failed_shop_ids = "failed_shop_ids"


class TextSaver(S3ReaderWriter):
    @property
    def s3_folder(self) -> str:
        return "text"

    month_shop_df_columns = [
        "ad_id",
        "account_id",
        "shop_id",
        "primary",
        "description",
        "title",
        "target",
        "genders",
        "spend_USD",
    ]

    min_monthly_spend_USD = 100
    save_every_n_shops = 15
    top_n_ads_per_shop = 5

    @property
    def end_date(self) -> date:
        return date.today()

    def get_month_shop_df(self, db: Session, first_day_of_month: date, shop_id: int) -> pd.DataFrame:
        last_day_of_month = get_last_day_of_this_month(dt=first_day_of_month)
        shop_month_df = ping_facebook_creative_target_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=first_day_of_month,
            end_date=last_day_of_month,
            period=Period.all,
        )
        return shop_month_df[self.month_shop_df_columns]

    # def create_and_save_month_df(self, db: Session, first_day_of_month: date, testing: bool = False) -> pd.DataFrame:
    #     month_df = pd.DataFrame()
    #     logger.info(f"Saving month_df for month {first_day_of_month}")
    #     if not testing:
    #         shops = crud.shop.get_nontest_shops(db=db)
    #         shop_ids =

    #     for shop_ in shops:
    #         shop_month_df = self.get_month_shop_df(
    #             db=db, first_day_of_month=first_day_of_month, shop_id=shop_.id
    #         )
    #         month_df = pd.concat([month_df, shop_month_df], axis=0)

    #     self.save_df(df=month_df, df_type=TextDF.month, df_id=first_day_of_month.strftime("%Y-%m"))
