import pandas as pd
from tqdm import tqdm

from loguru import logger

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import add_two_dicts
from src.s3.utils import read_csv_from_s3, save_csv_to_s3, read_image_from_s3, list_objects_from_prefix

db = SessionLocal()


def add_global_centroids(
    self,
    n_iterations_between_save: int = 300,
    force_from_scratch: bool = False,
):
    table_path = self.image_df

    image_df = read_csv_from_s3(self.image_df)
    perf_df = read_csv_from_s3(self.url_performance_df)
    full_df = perf_df.merge(image_df, on="url")

    if force_from_scratch or "global_color_centroids" not in image_df.columns:
        image_df["global_color_centroids"] = None

    basic_colors = calculate_basic_colors(full_df=full_df, n_clusters=self.n_global_centroids)
    logger.debug(f"len basic colors: {len(basic_colors)}")
    nn = train_nn_on_basic_colors(basic_colors=basic_colors)

    for idx, row in tqdm(image_df.iterrows(), total=len(image_df)):
        if row["uploaded"] is False or type(row["global_color_centroids"]) == dict:
            continue
        img = read_image_from_s3(path=f'{self.image_folder}/{row["uuid"]}.png')
        img_projected_to_basic_colors = project_image_onto_basic_colors(
            img=img, nn=nn, n_pixels=self.n_pixels, plot=False
        )
        unpacked_img = img_projected_to_basic_colors.reshape(-1, 3).tolist()
        color_centroids = dict(Counter(map(tuple, unpacked_img)))
        try:
            assert all([color in basic_colors for color in color_centroids.keys()])
        except Exception:
            logger.debug(basic_colors)
            logger.debug([col for col in color_centroids.keys() if col not in basic_colors])
        image_df.loc[idx, "global_color_centroids"] = [color_centroids]

        if idx % n_iterations_between_save == 5:
            image_df.global_color_centroids = image_df.global_color_centroids.apply(
                lambda x: x[0] if type(x) == list and len(x) else x
            )
            save_csv_to_s3(df=image_df, path=table_path, index=False)

    image_df.global_color_centroids = image_df.global_color_centroids.apply(
        lambda x: x[0] if type(x) == list and len(x) else x
    )

    save_csv_to_s3(df=image_df, path=table_path, index=False)


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
    basic_colors = clf.cluster_centers_
    return basic_colors
