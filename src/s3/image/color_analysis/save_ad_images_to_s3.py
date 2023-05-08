import pandas as pd
from tqdm import tqdm

from loguru import logger

from src.database.session import SessionLocal
from src.models import *
from src.utils import *

db = SessionLocal()


def save_ad_images_to_s3(
    self,
    image_df: pd.DataFrame | None = None,
    n_iterations_between_save: int = 500,
):
    table_path = self.image_df
    if image_df is None:
        image_df = read_csv_from_s3(table_path)

    logger.debug(image_df)

    for idx, row in tqdm(image_df.iterrows(), total=len(image_df)):
        if type(row["uploaded"]) is bool:
            continue
        url = row["url"]
        image = download_image_from_url(image_url=url)
        image = image.shrink_without_distortion(n_pixels=self.n_pixels)
        save_image_to_s3(image=image, path=f'{self.image_folder}/{row["uuid"]}.png')

        image_df.loc[idx, "uploaded"] = image is not None

        if idx % n_iterations_between_save == 5:
            save_csv_to_s3(df=image_df, path=table_path, index=False)

    save_csv_to_s3(df=image_df, path=table_path, index=False)
