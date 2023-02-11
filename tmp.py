import pandas as pd
import numpy as np
from src.pingers import ping_ads_insights_all_platforms, ping_crm
from src.database.session import db
from src.s3 import read_csv_from_s3
from src.models import *
from app.authenticate import get_username_config


if __name__ == "__main__":
    # df = ping_ads_insights_all_platforms(db=db, get_industry=True)
    # # df.to_csv("data/ads_insights.csv", index=False)

    # # crm = read_csv_from_s3(bucket="lebesgue-crm", path="crm_dataset_dev.csv", add_global_path=False)
    # # crm = crm[["shop_id", "industry"]]
    # # crm.to_csv("industries.csv")

    # # query = db.query(FacebookAdsInsights.revenue).filter(FacebookAdsInsights.revenue.is_not(None)).limit(1)

    # # df = pd.read_sql(query.statement, db.bind)

    # # df = ping_crm()
    # print(df.industry.value_counts(dropna=False))
    # # for i in df.industry:
    # #     if type(i) != str:
    # #         print(np.isnan(i))

    # df = df[(df.tiktok_spend.notna()) & (df.facebook_spend.isna()) & (df.google_spend.isna())]
    # print(df)
    pass
