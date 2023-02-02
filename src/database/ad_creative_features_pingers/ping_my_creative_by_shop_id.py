import sys

sys.path.append("././.")

import pandas as pd
from datetime import date

from src.database.myDB import DBConnect

from src.database.session import SessionLocal
from src.database.models.facebook.ad_creative_features import AdCreativeFeatures


# def ping_my_creative_by_shop_id(shop_id: str | list[str]) -> pd.DataFrame:

#     cursor = DBConnect()

#     if type(shop_id) == str:
#         shop_id = [shop_id]

#     query = f"""
#         select *
#         from ad_creative_features
#         where shop_id in %s
#     """

#     variables = [tuple(shop_id)]

#     cursor.execute(query, variables)

#     data = cursor.fetchall()
#     cols = []

#     for elt in cursor.description:
#         cols.append(elt[0])

#     df = pd.DataFrame(data=data, columns=cols)

#     df.shop_id = df.shop_id.astype(str)

#     # unstacking
#     df.set_index(["ad_id", "shop_id", "account_id", "feature"], inplace=True)
#     df.drop(["creative_id"], axis=1, inplace=True)
#     df = df.unstack(level=-1)
#     df = df.droplevel(level=0, axis=1)
#     df = df.reset_index()
#     df.columns.name = None

#     return df


def ping_my_creative_by_shop_id(shop_id: str | list[str]) -> pd.DataFrame:

    session = SessionLocal()

    query = session.query(AdCreativeFeatures).filter_by(shop_id=shop_id)

    df = pd.read_sql(query.statement, session.bind)

    df.shop_id = df.shop_id.astype(str)

    # unstacking
    df.set_index(["ad_id", "shop_id", "account_id", "feature"], inplace=True)
    df.drop(["creative_id"], axis=1, inplace=True)
    df = df.unstack(level=-1)
    df = df.droplevel(level=0, axis=1)
    df = df.reset_index()
    df.columns.name = None

    return df


def main():
    df = ping_my_creative_by_shop_id(shop_id="2")
    print(df)


if __name__ == "__main__":
    main()
