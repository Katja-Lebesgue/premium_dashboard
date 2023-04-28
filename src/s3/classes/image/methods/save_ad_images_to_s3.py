import pandas as pd
from tqdm import tqdm

from loguru import logger

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.s3.utils import read_csv_from_s3, save_csv_to_s3, save_image_to_s3

db = SessionLocal()


def save_ad_images_to_s3(
    self,
    image_df: pd.DataFrame | None = None,
    table_path: str = "data/fb_images/image.csv",
    image_folder_path: str = "data/fb_images/images",
    n_iterations_between_save: int = 30,
):
    if image_df is None:
        image_df = read_csv_from_s3(table_path)

    logger.debug(image_df)

    for idx, row in tqdm(image_df.iterrows(), total=len(image_df)):
        if type(row["uploaded"]) is bool:
            continue
        url = row["url"]
        img = download_image(img_url=url, convert_to_rgb=True)
        img = shrink_image_without_distortion(img, n_pixels=self.n_pixels)
        save_image_to_s3(img=img, path=f'{image_folder_path}/{row["uuid"]}.png')

        image_df.loc[idx, "uploaded"] = img is not None

        if idx % n_iterations_between_save == 5:
            save_csv_to_s3(df=image_df, path=table_path, index=False)

    save_csv_to_s3(df=image_df, path=table_path, index=False)
