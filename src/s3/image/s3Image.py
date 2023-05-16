from src.s3.image.color_analysis import *
from src.database.session import db
from sqlalchemy.orm import Session


class s3Image:
    fb_images_folder = "data/fb_images/"
    color_analysis_folder = fb_images_folder + "color_analysis/"
    image_folder = color_analysis_folder + "images_1000px"
    url_performance_df = fb_images_folder + "url_performance.csv"
    image_df = color_analysis_folder + "image.csv"
    top_n_ads_per_shop_and_month_by_spend = (
        color_analysis_folder + "top_n_ads_per_shop_and_month_by_spend.csv"
    )
    final_df = color_analysis_folder + "final.csv"
    final_by_shop_df = color_analysis_folder + "final_by_shop.csv"
    performance_columns = ["spend_USD", "impr", "link_clicks", "purch", "purch_value"]

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

    save_urls_and_performance_to_s3 = save_urls_and_performance_to_s3
    filter_and_save_top_n_ads_per_shop_and_month_by_spend = (
        filter_and_save_top_n_ads_per_shop_and_month_by_spend
    )
    update_image_df = update_image_df
    save_ad_images_to_s3 = save_ad_images_to_s3
    add_local_centroids = add_local_centroids
    add_global_centroids = add_global_centroids
    save_final = save_final

    def color_analysis(self):
        self.save_urls_and_performance_to_s3(force_from_scratch=True)
        self.filter_and_save_top_n_ads_per_shop_and_month_by_spend()
        self.update_image_df()
        self.save_ad_images_to_s3()
        self.add_local_centroids()
        self.add_global_centroids(force_from_scratch=True)
        self.save_final()


s3_image = s3Image(db=db)
