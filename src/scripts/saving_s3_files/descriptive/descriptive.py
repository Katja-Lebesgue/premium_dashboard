from datetime import date
from dateutil.relativedelta import relativedelta
import os
from abc import ABC, abstractmethod, abstractproperty

from tqdm import tqdm
from sqlalchemy.orm import Session

from src import crud
from src.utils import *


class Descriptive(ABC):
    # main function
    def save_to_s3(self, db: Session, end_date: date, force_from_scratch: bool = False):
        # end_date should be the last day of the month so we always
        # only consider data from full months
        end_date_plus_one = date(year=end_date.year, month=end_date.month, day=1)
        core_path = os.path.join(self.s3_folder, self.s3_file_name)
        table_path = core_path + ".csv"
        done_shop_ids_path = core_path + "_done_shop_ids" + ".csv"

        active_shops = crud.shop.get_all_active_shops(db=db)
        active_shop_ids = pd.Series([shop_.id for shop_ in active_shops]).sort_values()

        list_of_objects_on_s3 = list_objects_from_prefix(prefix=table_path)
        from_scratch = force_from_scratch or len(list_of_objects_on_s3) > 0

        if from_scratch:
            main_df = pd.DataFrame()
            undone_shop_ids = active_shop_ids
        else:
            main_df = read_csv_and_eval(path=table_path)
            main_df = main_df.set_index(self.main_df_index)
            done_shop_ids = read_csv_from_s3(path=done_shop_ids_path)["shop_id"]
            max_done_shop_id = max(done_shop_ids)
            undone_shop_ids = active_shop_ids[active_shop_ids > max_done_shop_id]

        start_date = end_date_plus_one - relativedelta(self.n_months)
        end_date = end_date_plus_one - timedelta(days=1)

        n_unsaved_shops = 0
        for shop_id in tqdm(undone_shop_ids):
            if n_unsaved_shops == self.save_every_n_shops:
                save_csv_to_s3(df=main_df, path=table_path, index=True)
                save_csv_to_s3(df=done_shop_ids, path=done_shop_ids_path)
                n_unsaved_shops = 0

            shop_descriptive_df = self.get_shop_descriptive_df(
                db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
            )

            if len(shop_descriptive_df):
                main_df = main_df.add(shop_descriptive_df, fill_value=0)
                n_unsaved_shops += 1
        save_csv_to_s3(df=main_df, path=table_path, index=True)
        save_csv_to_s3(df=done_shop_ids, path=done_shop_ids_path)

    def get_shop_descriptive_df(
        self, db: Session, shop_id: int, start_date: date, end_date: date
    ) -> pd.DataFrame:
        shop_df = self.get_shop_df(db=db, shop_id=shop_id, start_date=start_date, end_date=end_date)
        shop_df["n_ads"] = 1
        shop_descriptive_df = pd.DataFrame()
        if not len(shop_df) or not all(
            [col in shop_df.columns for col in self.descriptive_columns + self.metric_columns]
        ):
            return shop_descriptive_df

        for descriptive_column in self.descriptive_columns:
            filtered = shop_df.loc[:, ["year_month", descriptive_column] + self.metric_columns].rename(
                columns={descriptive_column: "feature_value"}
            )
            sum_by_month = filtered.groupby("year_month").sum()
            grouped = filtered.groupby(
                [
                    "year_month",
                    "feature_value",
                ]
            )

            absolute_sum_df = grouped.sum().loc[:, self.metric_columns]
            relative_sum_df = (absolute_sum_df / sum_by_month).rename(
                columns=lambda col_name: col_name + "_by_shop"
            )

            descriptive_column_df = absolute_sum_df.join(relative_sum_df)
            descriptive_column_df["feature"] = descriptive_column
            descriptive_column_df = descriptive_column_df.set_index(["feature"], append=True)
            descriptive_column_df = descriptive_column_df.reorder_levels(self.main_df_index, axis=0).fillna(0)
            shop_descriptive_df = pd.concat([shop_descriptive_df, descriptive_column_df], axis=0)

        shop_descriptive_df["n_shops"] = (shop_descriptive_df.n_ads > 0).astype(int)
        return shop_descriptive_df

    # abstract properties and methods
    @abstractproperty
    def s3_folder(self) -> str:
        ...

    @abstractproperty
    def descriptive_columns(self) -> list[str]:
        ...

    @abstractmethod
    def s3_file_name(self, end_date) -> str:
        ...

    @abstractmethod
    def get_shop_df(db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        ...

    # concrete properties and methods
    n_months = 24
    metric_columns = ["spend_USD", "impr", "link_clicks", "purch"]
    save_every_n_shops = 15
    main_df_index = ["year_month", "feature", "feature_type"]
