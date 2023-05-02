from src.s3.image.methods import *


class s3Image:
    global_folder = "data/fb_images/"
    image_folder = global_folder + "images"
    url_performance_df = global_folder + "url_performance.csv"
    image_df = global_folder + "image.csv"
    top_n_ads_per_shop_and_month_by_spend = global_folder + "top_n_ads_per_shop_and_month_by_spend.csv"
    final_df = global_folder + "final.csv"
    final_by_shop_df = global_folder + "final_by_shop.csv"
    performance_columns = ["spend_USD", "impr", "link_clicks", "purch", "purch_value"]

    def __init__(
        self,
        n_pixels: int = 1000,
        n_local_centroids: int = 5,
        n_global_centroids: int = 12,
        n_ads_per_shop_and_month: int = 5,
    ):
        self.n_ads_per_shop_and_month = n_ads_per_shop_and_month
        self.n_pixels = n_pixels
        self.n_local_centroids = n_local_centroids
        self.n_global_centroids = n_global_centroids

    save_urls_and_performance_to_s3 = save_urls_and_performance_to_s3
    filter_and_save_top_n_ads_per_shop_and_month_by_spend = (
        filter_and_save_top_n_ads_per_shop_and_month_by_spend
    )
    initialize_image_df = initialize_image_df
    save_ad_images_to_s3 = save_ad_images_to_s3
    add_local_centroids = add_local_centroids
    add_global_centroids = add_global_centroids
    save_final = save_final


s3_image = s3Image()
