from src.pingers import ping_ads_insights_all_platforms
from src.database.session import db


if __name__ == "__main__":
    df = ping_ads_insights_all_platforms(db=db, get_industry=True)
    df.to_csv("data/ads_insights.csv", index=False)
