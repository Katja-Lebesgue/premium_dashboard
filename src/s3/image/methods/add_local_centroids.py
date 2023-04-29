import pandas as pd
from tqdm import tqdm

from loguru import logger

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import *

db = SessionLocal()


def add_local_centroids(
    self,
    image_df: pd.DataFrame | None = None,
    n_iterations_between_save: int = 300,
    force_from_scratch: bool = False,
):
    table_path = self.image_df
    if image_df is None:
        image_df = read_csv_from_s3(table_path)

    logger.debug(image_df)

    if force_from_scratch or "local_color_centroids" not in image_df.columns:
        image_df["local_color_centroids"] = None
    i = 0
    for idx, row in tqdm(image_df.iterrows(), total=len(image_df)):
        if row["uploaded"] is False or type(row["local_color_centroids"]) == dict:
            continue
        img = read_image_from_s3(path=f'{self.image_folder}/{row["uuid"]}.png')
        color_centroids = color_analysis(img=img, n_clusters=self.n_local_centroids, n_pixels=self.n_pixels)
        image_df.loc[idx, "local_color_centroids"] = [color_centroids]
        i += 1
        if i % n_iterations_between_save == 5:
            image_df.local_color_centroids = image_df.local_color_centroids.apply(
                lambda x: x[0] if type(x) == list and len(x) else x
            )
            save_csv_to_s3(df=image_df, path=table_path, index=False)
    image_df.local_color_centroids = image_df.local_color_centroids.apply(
        lambda x: x[0] if type(x) == list and len(x) else x
    )
    save_csv_to_s3(df=image_df, path=table_path, index=False)
