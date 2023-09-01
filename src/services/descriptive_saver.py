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
from src.abc.descriptive import *


class DescriptiveSaver(Descriptive):
    save_every_n_shops = 15

    def create_and_save_summary(self, end_date: date | None = None) -> pd.DataFrame:
        main_df = self.read_df(df_type=DescriptiveDF.main, end_date=end_date)
        main_df["n_shops"] = 1
        sum_by_shop_and_feature = main_df.groupby(["shop_id", "year_month", "feature"])[
            self.metric_columns
        ].sum()
        grouped_by_shop_and_value = main_df.groupby(["shop_id", "year_month", "feature", "feature_value"])

        absolute_sum_by_shop_and_value = grouped_by_shop_and_value[self.metric_columns + ["n_shops"]].sum()
        relative_sum_by_shop_and_value = (
            absolute_sum_by_shop_and_value[self.metric_columns] / sum_by_shop_and_feature
        )
        relative_sum_by_value = (
            relative_sum_by_shop_and_value.reset_index()
            .groupby(["year_month", "feature", "feature_value"])[self.metric_columns]
            .sum()
        )
        n_shops_by_month_and_feature = (
            relative_sum_by_value.reset_index().groupby(["year_month", "feature"])[self.metric_columns].sum()
        )
        normalised_relative_sum_by_value = relative_sum_by_value.div(n_shops_by_month_and_feature, axis=0)
        normalised_relative_sum_by_value.rename(
            columns={col: col + "_by_shop" for col in self.metric_columns}, inplace=True
        )
        absolute_sum_by_value = (
            absolute_sum_by_shop_and_value.reset_index()
            .groupby(["year_month", "feature", "feature_value"])
            .sum()
        )
        summary_df = absolute_sum_by_value.join(normalised_relative_sum_by_value)
        self.save_df(df=summary_df, df_type=DescriptiveDF.summary, end_date=end_date, index=True)
        return summary_df

    # main function
    def create_and_save_main(
        self,
        db: Session,
        force_from_scratch: bool = False,
        repeat_for_failed: bool = False,
        df_type: str = DescriptiveDF.main,
        testing: bool = False,
    ) -> pd.DataFrame:
        all_shops = crud.shop.get_nontest_shops(db=db)
        all_shop_ids = pd.Series([shop_.id for shop_ in all_shops], name="shop_id").sort_values()

        list_of_objects_on_s3 = list_objects_from_prefix(
            prefix=self.get_df_path(df_type=df_type, end_date=self.end_date)
        )

        from_scratch = force_from_scratch or len(list_of_objects_on_s3) == 0

        if from_scratch:
            main_df = pd.DataFrame()
            done_shop_ids = pd.Series([], name="shop_id")
            failed_shop_ids = pd.Series([], name="shop_id")
            undone_shop_ids = all_shop_ids
        else:
            main_df = self.read_df(df_type=df_type, end_date=self.end_date).set_index(self.main_df_index)
            done_shop_ids = self.read_df(df_type=DescriptiveDF.done_shop_ids, end_date=self.end_date)[
                "shop_id"
            ]
            failed_shop_ids = self.read_df(df_type=DescriptiveDF.failed_shop_ids, end_date=self.end_date)[
                "shop_id"
            ]
            logger.debug(f"{failed_shop_ids = }")
            max_done_shop_id = max(done_shop_ids)
            undone_shop_ids = all_shop_ids[all_shop_ids > max_done_shop_id]

        if repeat_for_failed:
            undone_shop_ids = pd.concat([failed_shop_ids, undone_shop_ids])

        new_failed_shop_ids = []
        new_done_shop_ids = []

        if testing:
            undone_shop_ids = [16038, 44301396, 34810574]

        n_unsaved_shops = 0
        shop_loader = tqdm(undone_shop_ids)
        for shop_id in shop_loader:
            if n_unsaved_shops == self.save_every_n_shops:
                self.save_df(df=main_df, df_type=df_type, index=True, end_date=self.end_date)
                self.save_df(
                    df=pd.concat([done_shop_ids, pd.Series(new_done_shop_ids, name="shop_id")]),
                    df_type=DescriptiveDF.done_shop_ids,
                    index=False,
                    end_date=self.end_date,
                )
                self.save_df(
                    df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
                    df_type=DescriptiveDF.failed_shop_ids,
                    index=False,
                    end_date=self.end_date,
                )
                new_failed_shop_ids = []
                new_done_shop_ids = []
                n_unsaved_shops = 0

            try:
                shop_descriptive_df = self.get_shop_descriptive_df(
                    db=db, shop_id=shop_id, start_date=self.start_date, end_date=self.end_date
                )

                shop_loader.set_postfix({"shop_id": str(shop_id), "len": len(shop_descriptive_df)})

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

        self.save_df(df=main_df, df_type=df_type, index=True, end_date=self.end_date)
        self.save_df(
            df=pd.concat([done_shop_ids, pd.Series(new_done_shop_ids, name="shop_id")]),
            df_type=DescriptiveDF.done_shop_ids,
            index=False,
            end_date=self.end_date,
        )
        self.save_df(
            df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
            df_type=DescriptiveDF.failed_shop_ids,
            index=False,
            end_date=self.end_date,
        )

        return main_df

    def save_df(
        self, df: pd.DataFrame, df_type: DescriptiveDF, end_date: date | None = None, index: bool = True
    ):
        return save_csv_to_s3(df=df, path=self.get_df_path(df_type=df_type, end_date=end_date), index=index)


class FacebookCreativeDescriptiveSaver(DescriptiveSaver, FacebookCreativeDescriptive):
    ...


class FacebookTargetDescriptiveSaver(DescriptiveSaver, FacebookTargetDescriptive):
    ...


class GoogleCampaignTypeDescriptiveSaver(DescriptiveSaver, GoogleCampaignTypeDescriptive):
    ...


facebook_creative_descriptive_saver = FacebookCreativeDescriptiveSaver()
facebook_target_descriptive_saver = FacebookTargetDescriptiveSaver()
google_campaign_type_descriptive_saver = GoogleCampaignTypeDescriptiveSaver()
