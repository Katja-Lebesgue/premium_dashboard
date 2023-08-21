from datetime import date
from dateutil.relativedelta import relativedelta
import os
from abc import ABC, abstractmethod, abstractproperty

from loguru import logger

from tqdm import tqdm
from sqlalchemy.orm import Session
import re

from src.abc.descriptive import Descriptive, DescriptiveDF
from src import crud
from src.utils import *


class DescriptiveSaver(Descriptive):
    def create_and_save_summary(self, end_date: date) -> None:
        main_df = self.read_df(df_type=DescriptiveDF.main, end_date=end_date)
        main_df["n_shops"] = 1
        sum_by_month_and_feature = main_df.groupby(["year_month", "feature"])[self.metric_columns].sum()
        grouped = main_df.groupby(["year_month", "feature", "feature_value"])

        absolute_sum_df = grouped[self.metric_columns + ["n_shops"]].sum()

        relative_sum_df = (absolute_sum_df / sum_by_month_and_feature)[self.metric_columns].rename(
            columns={col: col + "_by_shop" for col in self.metric_columns}
        )
        summary_df = absolute_sum_df.join(relative_sum_df)
        self.save_df(df=summary_df, df_type=DescriptiveDF.summary, end_date=end_date)

    # main function
    def create_and_save_main(
        self, db: Session, end_date: date, force_from_scratch: bool = False, repeat_for_failed: bool = False
    ) -> None:
        # end_date should be the last day of the month so we always
        # only consider data from full months
        end_date_plus_one = date(year=end_date.year, month=end_date.month, day=1)
        start_date = end_date_plus_one - relativedelta(months=self.n_months)
        end_date = end_date_plus_one - timedelta(days=1)

        all_shops = crud.shop.get_nontest_shops(db=db)
        all_shop_ids = pd.Series([shop_.id for shop_ in all_shops], name="shop_id").sort_values()

        list_of_objects_on_s3 = list_objects_from_prefix(
            prefix=self.get_df_path(df_type=DescriptiveDF.main, end_date=end_date)
        )
        from_scratch = force_from_scratch or len(list_of_objects_on_s3) > 0

        if from_scratch:
            main_df = pd.DataFrame()
            done_shop_ids = pd.Series([], name="shop_id")
            failed_shop_ids = pd.Series([], name="shop_id")
            undone_shop_ids = all_shop_ids
        else:
            main_df = self.get_df(df_type=DescriptiveDF.main, end_date=end_date)
            done_shop_ids = self.get_df(df_type=DescriptiveDF.done_shop_ids, end_date=end_date)["shop_id"]
            failed_shop_ids = self.get_df(df_type=DescriptiveDF.failed_shop_ids, end_date=end_date)["shop_id"]
            logger.debug(f"{failed_shop_ids = }")
            max_done_shop_id = max(done_shop_ids)
            undone_shop_ids = all_shop_ids[all_shop_ids > max_done_shop_id]

        if repeat_for_failed:
            undone_shop_ids = pd.concat([failed_shop_ids, undone_shop_ids])

        new_failed_shop_ids = []
        new_done_shop_ids = []

        # FOR DEBUGGING
        undone_shop_ids = [16038, 44301396]
        n_unsaved_shops = 0
        for shop_id in tqdm(undone_shop_ids):
            if n_unsaved_shops == self.save_every_n_shops:
                self.save_df(df=main_df, df_type=DescriptiveDF.main, index=False, end_date=end_date)
                self.save_df(
                    df=pd.concat([done_shop_ids, pd.Series(new_done_shop_ids, name="shop_id")]),
                    df_type=DescriptiveDF.done_shop_ids,
                    index=False,
                    end_date=end_date,
                )
                self.save_df(
                    df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
                    df_type=DescriptiveDF.failed_shop_ids,
                    index=False,
                    end_date=end_date,
                )
                new_failed_shop_ids = []
                new_done_shop_ids = []
                n_unsaved_shops = 0

            try:
                shop_descriptive_df = self.get_shop_descriptive_df(
                    db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
                )

                if len(shop_descriptive_df):
                    if not (len(main_df)):
                        main_df = shop_descriptive_df
                    else:
                        # main_df = main_df.add(shop_descriptive_df, fill_value=0)
                        main_df = pd.concat([main_df, shop_descriptive_df], axis=0)
                n_unsaved_shops += 1
                new_done_shop_ids.append(shop_id)
            except Exception as e:
                logger.error(f"Error for shop id {shop_id}: \n {e}")
                new_failed_shop_ids.append(shop_id)

        self.save_df(df=main_df, df_type=DescriptiveDF.main, index=True, end_date=end_date)
        self.save_df(
            df=pd.concat([done_shop_ids, pd.Series(new_done_shop_ids, name="shop_id")]),
            df_type=DescriptiveDF.done_shop_ids,
            index=False,
            end_date=end_date,
        )
        self.save_df(
            df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
            df_type=DescriptiveDF.failed_shop_ids,
            index=False,
            end_date=end_date,
        )

    def get_shop_descriptive_df(
        self, db: Session, shop_id: int, start_date: date, end_date: date
    ) -> pd.DataFrame:
        shop_df = self.get_shop_df(db=db, shop_id=shop_id, start_date=start_date, end_date=end_date)
        shop_df["n_ads"] = 1
        shop_descriptive_df = pd.DataFrame()

        if not len(shop_df):
            logger.debug(f"{shop_id}: -")
            return shop_descriptive_df

        logger.debug(f"{shop_id}: +")

        if len(
            (
                missing_columns := [
                    col
                    for col in self.descriptive_columns + self.metric_columns
                    if col not in shop_df.columns
                ]
            )
        ):
            logger.debug(f"{missing_columns = }")
            return shop_descriptive_df

        shop_df[self.fake_feature] = "."
        for descriptive_column in self.descriptive_columns + [self.fake_feature]:
            filtered = shop_df.loc[:, ["year_month", descriptive_column] + self.metric_columns].rename(
                columns={descriptive_column: "feature_value"}
            )

            if descriptive_column in self.explode_descriptive_columns:
                filtered = filtered.explode("feature_value").dropna(axis=0, subset="feature_value")
            descriptive_column_df = (
                filtered.groupby(["year_month", "feature_value"])[self.metric_columns].sum().reset_index()
            )
            descriptive_column_df["feature"] = descriptive_column

            descriptive_column_df["shop_id"] = shop_id
            shop_descriptive_df = pd.concat([shop_descriptive_df, descriptive_column_df], axis=0)

        return shop_descriptive_df

    # abstract properties and methods

    @abstractmethod
    def get_shop_df(db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        ...

    # concrete properties and methods

    # TODO: change to 24 after testing is over
    n_months = 24

    save_every_n_shops = 15
    main_df_index = ["year_month", "feature", "feature_value"]

    def save_df(self, df: pd.DataFrame, df_type: DescriptiveDF, end_date: date, index: bool = True):
        return save_csv_to_s3(df=df, path=self.get_df_path(df_type=df_type, end_date=end_date), index=index)
