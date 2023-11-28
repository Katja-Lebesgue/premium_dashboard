import os
from abc import abstractproperty
from datetime import date

from tqdm import tqdm

from src.models import *
from src import crud
from src.utils import *


class S3ReaderWriter:
    save_every_n_shops = 15
    skip_shop_ids = []

    @abstractproperty
    def s3_folder(self) -> str:
        ...

    def get_df_path(self, df_type: str, df_id: str):
        return os.path.join(self.s3_folder, f"{df_type}_{df_id}.csv")

    def read_df(self, df_type: str, df_id: str):
        logger.debug(f"####: {self.get_df_path(df_type=df_type, df_id=df_id)}")
        return read_csv_from_s3(path=self.get_df_path(df_type=df_type, df_id=df_id))

    def save_df(self, df: pd.DataFrame, index: bool = True, **kwargs):
        logger.debug(f"aha: {kwargs}")
        return save_csv_to_s3(df=df, path=self.get_df_path(**kwargs), index=index)

    def save_for_all_shops(
        self,
        db: Session,
        df_type: str,
        df_id: str,
        all_shops: list[Shop] | None = None,
        force_from_scratch: bool = False,
        repeat_for_failed: bool = False,
        save_to_s3: bool = True,
        testing: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        failed_shops_df_type = f"{df_type}_failed_shop_ids"
        if all_shops is None:
            all_shops = crud.shop.get_nontest_shops(db=db)
        logger.info(f"Total of {len(all_shops)} shops.")

        all_shop_ids = sorted([shop_.id for shop_ in all_shops if shop_.id not in self.skip_shop_ids])

        if testing:
            all_shop_ids = sorted([16038, 44301396, 34810574, 96200, 2])
            all_shop_ids = sorted([16038, 96200])

        if not force_from_scratch:
            list_of_objects_on_s3 = list_objects_from_prefix(
                prefix=self.get_df_path(df_type=df_type, df_id=df_id)
            )
            logger.debug(list_of_objects_on_s3)
            from_scratch = force_from_scratch or len(list_of_objects_on_s3) == 0
        else:
            from_scratch = True

        if from_scratch:
            main_df = pd.DataFrame()
            failed_shop_ids = pd.Series([], name="shop_id")
            undone_shop_ids = all_shop_ids
        else:
            main_df = self.read_df(df_type=df_type, df_id=df_id)
            done_shop_ids = main_df.shop_id.unique().tolist()
            failed_shop_ids = self.read_df(df_type=failed_shops_df_type, df_id=df_id)["shop_id"]
            max_done_shop_id = max(done_shop_ids)
            logger.info(f"{max_done_shop_id = }")
            undone_shop_ids = [shop_id for shop_id in all_shop_ids if shop_id > max_done_shop_id]
        if repeat_for_failed:
            undone_shop_ids = failed_shop_ids.tolist() + undone_shop_ids

        new_failed_shop_ids = []
        n_unsaved_shops = 0
        shop_loader = tqdm(undone_shop_ids)

        for shop_id in shop_loader:
            if save_to_s3 and n_unsaved_shops == self.save_every_n_shops:
                self.save_df(df=main_df, df_type=df_type, df_id=df_id, index=False)
                self.save_df(
                    df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
                    df_type=failed_shops_df_type,
                    df_id=df_id,
                    index=False,
                )
                new_failed_shop_ids = []
                n_unsaved_shops = 0

            try:
                shop_loader.set_postfix({"shop_id": str(shop_id)})
                shop_df = self.get_shop_df(db=db, df_type=df_type, df_id=df_id, shop_id=shop_id, **kwargs)

                if len(shop_df):
                    if not len(main_df):
                        main_df = shop_df
                    else:
                        main_df = pd.concat([main_df, shop_df], axis=0)
                n_unsaved_shops += 1
            except Exception as e:
                logger.error(f"Error for shop id {shop_id}: \n {e}")
                new_failed_shop_ids.append(shop_id)
        logger.debug(f"{len(main_df) = }")
        if save_to_s3:
            self.save_df(df=main_df, df_type=df_type, df_id=df_id, index=False)
            self.save_df(
                df=pd.concat([failed_shop_ids, pd.Series(new_failed_shop_ids, name="shop_id")]),
                df_type=failed_shops_df_type,
                df_id=df_id,
                index=False,
            )

        return main_df

    def get_shop_df(**kwargs) -> pd.DataFrame:
        ...

    def get_available_dates(self, df_type: str) -> list[date]:
        all_objects = list_objects_from_prefix(prefix=self.s3_folder)
        list_of_objects = [obj for obj in all_objects if df_type in obj]
        return [to_date(date_str) for date_str in extract_dates_from_str(" ".join(list_of_objects))]
