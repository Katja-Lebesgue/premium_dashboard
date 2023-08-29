from datetime import date, datetime

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session
from tqdm import tqdm
import uuid

from src.models import *
from src.utils import *
from src.database.session import db
from src.services.descriptive_saver import DescriptiveSaver
from src.abc.descriptive import *
from sqlalchemy.orm import Session


class FacebookImageDescriptiveSaver(DescriptiveSaver, FacebookImageDescriptive):
    save_every_n_shops = 15
    save_every_n_rows = 500

    @property
    def s3_image_folder(self):
        return os.path.join(self.s3_descriptive_folder, self.tag, "images")

    def __init__(
        self,
        db: Session,
        n_pixels: int = 1000,
        n_local_centroids: int = 5,
        n_global_centroids: int = 12,
        n_ads_per_shop_and_month: int = 5,
    ):
        self.n_ads_per_shop_and_month = n_ads_per_shop_and_month
        self.n_pixels = n_pixels
        self.n_local_centroids = n_local_centroids
        self.n_global_centroids = n_global_centroids
        self.db = db

    def save_everything(self, force_from_scratch: bool = False) -> None:
        self.create_and_save_performance(db=db, force_from_scratch=force_from_scratch)
        self.filter_and_save_top_n_ads_per_shop_and_month_by_spend()
        self.update_image_df(force_from_scratch=force_from_scratch)
        self.save_ad_images_to_s3(force_from_scratch=force_from_scratch)
        self.add_local_centroids(force_from_scratch=force_from_scratch)
        self.filter_image_df()
        self.add_global_centroids(force_from_scratch=force_from_scratch)
        self.create_and_save_main()
        self.create_and_save_summary()

    def create_and_save_performance(self, **kwargs) -> None:
        super().create_and_save_main(df_type=FacebookImageDescriptiveDF.performance, **kwargs)

    def filter_and_save_top_n_ads_per_shop_and_month_by_spend(
        self,
    ):
        performance_df = self.read_df(df_type=FacebookImageDescriptiveDF.performance, end_date=self.end_date)

        if (performance_df.groupby("url").apply(lambda df: df.shop_id.nunique()) > 1).sum() != 0:
            logger.warning("some urls are used by more than one shop.")

        top_ads = (
            performance_df.groupby(["shop_id", "year_month"])
            .apply(lambda df: df.sort_values("spend_USD").tail(self.n_ads_per_shop_and_month))
            .reset_index(drop=True)
        )

        self.save_df(
            df=top_ads, df_type=FacebookImageDescriptiveDF.filtered, end_date=self.end_date, index=False
        )

    def update_image_df(self, force_from_scratch: bool = False):
        performance_df = self.read_df(df_type=FacebookImageDescriptiveDF.performance, end_date=self.end_date)

        list_of_objects = list_objects_from_prefix(
            prefix=self.get_df_path(df_type=FacebookImageDescriptiveDF.image, end_date=self.end_date)
        )
        logger.debug(list_of_objects)
        from_scratch = force_from_scratch or not len(list_of_objects)
        if not from_scratch:
            old_image_df = self.read_df(df_type=FacebookImageDescriptiveDF.image, end_date=self.end_date)
        else:
            old_image_df = pd.DataFrame(columns=["url", "uuid", "uploaded"])
            delete_from_s3(prefix=self.s3_image_folder, add_global_folder=True)

        new_urls = performance_df.loc[~performance_df.url.isin(old_image_df.url), "url"].unique()
        old_image_df = old_image_df[~old_image_df.url.isin(new_urls)]
        new_image_df = pd.DataFrame(new_urls, columns=["url"])
        new_image_df["uuid"] = new_image_df.url.apply(lambda x: uuid.uuid1())
        new_image_df["uploaded"] = None
        image_df = pd.concat([old_image_df, new_image_df], axis=0)

        logger.debug(f"old: {len(old_image_df)}, new: {len(new_image_df)}")

        self.save_df(
            df=image_df, df_type=FacebookImageDescriptiveDF.image, end_date=self.end_date, index=False
        )

    def save_ad_images_to_s3(self, force_from_scratch: bool = False):
        self.add_column_to_df(
            df_type=FacebookImageDescriptiveDF.image,
            column_name="uploaded",
            force_from_scratch=force_from_scratch,
            func_for_row=self.save_image_for_row,
            save_index=False,
        )

    def add_local_centroids(self, force_from_scratch: bool = False) -> None:
        self.add_column_to_df(
            df_type=FacebookImageDescriptiveDF.image,
            force_from_scratch=force_from_scratch,
            column_name="local_color_centroids",
            func_for_row=self.calculate_local_centroids,
            save_index=False,
        )

    def filter_image_df(self):
        image_df = self.read_df(df_type=FacebookImageDescriptiveDF.image)
        image_df = image_df[image_df.local_color_centroids.apply(type) == dict]
        image_df = image_df[image_df.local_color_centroids.apply(len) > 0]
        self.save_df(df=image_df, df_type=FacebookImageDescriptiveDF.filtered_image)

    def add_global_centroids(self, force_from_scratch: bool = False) -> None:
        image_df = self.read_df(df_type=FacebookImageDescriptiveDF.filtered_image, end_date=self.end_date)
        perf_df = self.read_df(df_type=FacebookImageDescriptiveDF.performance, end_date=self.end_date)
        full_df = perf_df.merge(image_df, on="url")

        basic_colors = calculate_basic_colors(full_df=full_df, n_clusters=self.n_global_centroids)
        logger.debug(f"{len(basic_colors) = }")
        nn = MyNN(n_neighbors=1, algorithm="brute")
        nn.fit(basic_colors)
        self.add_column_to_df(
            df_type=FacebookImageDescriptiveDF.filtered_image,
            column_name="global_color_centroids",
            force_from_scratch=force_from_scratch,
            func_for_row=self.calculate_global_centroids,
            save_index=False,
            nn=nn,
        )

    def add_column_to_df(
        self,
        df_type: FacebookImageDescriptiveDF,
        column_name: str,
        func_for_row: Callable,
        force_from_scratch: bool = False,
        save_index: bool = True,
        **kwargs,
    ) -> None:
        df = self.read_df(df_type=df_type, end_date=self.end_date)

        if force_from_scratch or column_name not in df.columns:
            df[column_name] = None
        n_unsaved_rows = 0
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            if row[column_name] is not None:
                continue
            if n_unsaved_rows == self.save_every_n_rows:
                self.save_df(df=df, df_type=df_type, index=save_index)
            df.at[idx, column_name] = func_for_row(row=row, **kwargs)
            n_unsaved_rows += 1

        self.save_df(df=df, df_type=df_type, index=save_index, end_date=self.end_date)

    def save_image_for_row(self, row: dict) -> bool:
        image = download_image_from_url(image_url=row["url"])
        if image is None:
            return False
        image = image.shrink_without_distortion(n_pixels=self.n_pixels)
        self.save_image(image=image, uuid=row["uuid"])
        return True

    def calculate_local_centroids(self, row: dict) -> list:
        if row["uploaded"] is not True:
            return None
        image = self.read_image(uuid=row["uuid"])
        return image.color_analysis(n_clusters=self.n_local_centroids, n_pixels=self.n_pixels)

    def calculate_global_centroids(self, row: dict, nn: MyNN) -> list:
        if row["uploaded"] is not True:
            return None
        image = self.read_image(uuid=row["uuid"])
        image_projected_to_basic_colors = image.project_onto_basic_colors(
            nn=nn, n_pixels=self.n_pixels, plot=False
        )
        unpacked_image = image_projected_to_basic_colors.rgb.reshape(-1, 3).tolist()
        return dict(Counter(map(tuple, unpacked_image)))

    def create_and_save_main(
        self,
    ):
        perf_df = self.read_df(df_type=FacebookImageDescriptiveDF.performance, end_date=self.end_date)
        image_df = self.read_df(df_type=FacebookImageDescriptiveDF.filtered_image, end_date=self.end_date)

        image_df = image_df[image_df.global_color_centroids.notna()]
        image_df.global_color_centroids = image_df.global_color_centroids.apply(
            lambda x: {rgb_to_hex(k): v for k, v in x.items()}
        )
        unpacked_colors = image_df.global_color_centroids.apply(pd.Series).fillna(0)
        scaled_colors = unpacked_colors.div(unpacked_colors.sum(axis=1), axis=0)
        image_df = image_df.join(scaled_colors)

        full_df = perf_df.merge(image_df, on="url")
        full_df = full_df[full_df.shop_id != 37673090]
        full_df["n_ads"] = 1
        color_cols = [col for col in full_df.columns if col[0] == "#"]
        full_df = full_df[["ad_id", "shop_id", "year_month"] + self.metric_columns + color_cols]
        noncolor_cols = [col for col in full_df.columns if col[0] != "#"]
        stacked_df = full_df.set_index(noncolor_cols).stack(level=0).reset_index()
        level_col = [col for col in stacked_df.columns if "level" in str(col)][0]
        stacked_df = stacked_df.rename(columns={level_col: "color", 0: "freq"})
        stacked_df[self.metric_columns] = stacked_df[self.metric_columns].multiply(stacked_df.freq, axis=0)
        stacked_color_df = (
            stacked_df.rename(columns={"color": "feature_value"})
            .drop(columns=["freq"])
            .assign(feature="color")
        )
        stacked_color_df = (
            stacked_color_df.groupby(self.main_df_index + ["shop_id"])[self.metric_columns]
            .sum()
            .reset_index()
        )

        # adding fake feature
        fake_feature_df = full_df.groupby(["shop_id", "year_month"])[self.metric_columns].sum().reset_index()
        fake_feature_df["feature"] = self.fake_feature
        fake_feature_df["feature_value"] = "."

        full_stacked_df = pd.concat([stacked_color_df, fake_feature_df], axis=0)

        self.save_df(
            df=full_stacked_df, df_type=FacebookImageDescriptiveDF.main, end_date=self.end_date, index=False
        )

    def read_image(self, uuid: str) -> MyImage:
        return read_image_from_s3(path=os.path.join(self.s3_image_folder, f"{uuid}.png"))

    def save_image(self, image: MyImage, uuid: str) -> None:
        save_image_to_s3(image=image, path=os.path.join(self.s3_image_folder, f"{uuid}.png"))


def calculate_basic_colors(full_df: pd.DataFrame, n_clusters: int = 12) -> np.array:
    full_df["local_color_centroids_scaled_with_spend"] = full_df.apply(
        lambda full_df: {k: v * full_df.spend for k, v in full_df.local_color_centroids.items()}
        if full_df.uploaded == True
        else None,
        axis=1,
    )
    all_colors_packed = full_df.local_color_centroids_scaled_with_spend.apply(
        lambda x: [list(y) for y in x.items()] if type(x) == dict else []
    )
    all_colors_unpacked = sum(all_colors_packed, [])
    color_df = pd.DataFrame(all_colors_unpacked, columns=["color", "weight"])
    color_df = color_df.groupby("color")["weight"].sum().reset_index()
    color_df.weight = color_df.weight.div(color_df.weight.std())
    clf = KMeans(n_clusters=n_clusters)
    clf.fit(np.array(color_df.color.tolist()), sample_weight=color_df.weight)
    basic_colors = np.array(clf.cluster_centers_).astype(int)
    return basic_colors


facebook_image_descriptive_saver = FacebookImageDescriptiveSaver(db=db)
