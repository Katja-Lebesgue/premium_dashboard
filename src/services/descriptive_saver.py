import os
import re
from abc import ABC, abstractmethod, abstractproperty
from datetime import date

from dateutil.relativedelta import relativedelta
from loguru import logger
from sqlalchemy.orm import Session
from tqdm import tqdm

from src import crud
from src.abc.descriptive import *
from src.abc.descriptive import Descriptive, DescriptiveDF
from src.utils import *


class DescriptiveSaver(Descriptive):
    save_every_n_shops = 15
    skip_shop_ids = []

    def create_and_save_summary(self, end_date: date | None = None) -> pd.DataFrame:
        main_df = self.read_df(df_type=DescriptiveDF.main, end_date=end_date)
        main_df["n_shops"] = 1

        absolute_sum_by_shop_and_value = main_df.set_index(
            ["shop_id", "year_month", "feature", "feature_value"]
        )[self.metric_columns + ["n_shops"]]

        # absolute monthly sums
        absolute_sum_by_value = main_df.groupby(["year_month", "feature", "feature_value"]).sum()[
            self.metric_columns + ["n_shops"]
        ]

        # get df of relative values by shop
        sum_by_shop_and_feature = main_df.groupby(["shop_id", "year_month", "feature"])[
            self.metric_columns
        ].sum()

        relative_sum_by_shop_and_value = (
            absolute_sum_by_shop_and_value[self.metric_columns] / sum_by_shop_and_feature
        )

        # get df of relative sums without shop
        relative_sum_by_value = (
            relative_sum_by_shop_and_value.reset_index()
            .groupby(["year_month", "feature", "feature_value"])[self.metric_columns]
            .sum()
        )

        # normalize them by dividing by numnber of shops per month per feature
        n_shops_by_month_and_feature = (
            relative_sum_by_value.reset_index().groupby(["year_month", "feature"])[self.metric_columns].sum()
        )
        normalised_relative_sum_by_value = relative_sum_by_value.div(n_shops_by_month_and_feature, axis=0)
        normalised_relative_sum_by_value.rename(
            columns={col: col + "_by_shop" for col in self.metric_columns}, inplace=True
        )

        # join the two to get the final result
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
        save_to_s3: bool = True,
        testing: bool = False,
    ) -> pd.DataFrame:
        all_shops = crud.shop.get_nontest_shops(db=db)
        logger.info(f"Total of {len(all_shops)} nontest shops.")
        all_shop_ids = pd.Series(
            [shop_.id for shop_ in all_shops if shop_.id not in self.skip_shop_ids], name="shop_id"
        ).sort_values()

        list_of_objects_on_s3 = list_objects_from_prefix(
            prefix=self.get_df_path(df_type=df_type, end_date=self.end_date)
        )

        from_scratch = force_from_scratch or len(list_of_objects_on_s3) == 0

        if from_scratch:
            main_df = pd.DataFrame()
            failed_shop_ids = pd.Series([], name="shop_id")
            undone_shop_ids = all_shop_ids
        else:
            main_df = self.read_df(df_type=df_type, end_date=self.end_date)
            done_shop_ids = main_df.shop_id.unique().tolist()
            main_df = main_df.set_index(self.main_df_index)
            failed_shop_ids = self.read_df(df_type=DescriptiveDF.failed_shop_ids, end_date=self.end_date)[
                "shop_id"
            ]
            logger.debug(f"{failed_shop_ids = }")
            max_done_shop_id = max(done_shop_ids)
            logger.info(f"{max_done_shop_id = }")
            undone_shop_ids = all_shop_ids[all_shop_ids > max_done_shop_id]

        if repeat_for_failed:
            undone_shop_ids = pd.concat([failed_shop_ids, undone_shop_ids])

        new_failed_shop_ids = []

        if testing:
            undone_shop_ids = [16038, 44301396, 34810574, 96200, 2]
            # undone_shop_ids = [16038]

        n_unsaved_shops = 0
        shop_loader = tqdm(undone_shop_ids)

        for shop_id in shop_loader:
            if save_to_s3 and n_unsaved_shops == self.save_every_n_shops:
                self.save_df(df=main_df, df_type=df_type, index=True, end_date=self.end_date)
                self.save_df(
                    df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
                    df_type=DescriptiveDF.failed_shop_ids,
                    index=False,
                    end_date=self.end_date,
                )
                new_failed_shop_ids = []
                n_unsaved_shops = 0

            try:
                shop_loader.set_postfix({"shop_id": str(shop_id)})
                shop_descriptive_df = self.get_shop_descriptive_df(
                    db=db, shop_id=shop_id, start_date=self.start_date, end_date=self.end_date
                )

                if len(shop_descriptive_df):
                    if not (len(main_df)):
                        main_df = shop_descriptive_df
                    else:
                        main_df = pd.concat([main_df, shop_descriptive_df], axis=0)
                n_unsaved_shops += 1
            except Exception as e:
                logger.error(f"Error for shop id {shop_id}: \n {e}")
                new_failed_shop_ids.append(shop_id)

        if save_to_s3:
            self.save_df(df=main_df, df_type=df_type, index=True, end_date=self.end_date)
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
    skip_shop_ids = [42787782]


facebook_creative_descriptive_saver = FacebookCreativeDescriptiveSaver()
facebook_target_descriptive_saver = FacebookTargetDescriptiveSaver()
google_campaign_type_descriptive_saver = GoogleCampaignTypeDescriptiveSaver()
