import pandas as pd
from datetime import date

from src.database.myDB import DBConnect


def ping_my_creative_shop_ids() -> pd.DataFrame:

    cursor = DBConnect()

    query = f"""
        select distinct shop_id
        from ad_creative_features
    """

    cursor.execute(query)

    data = cursor.fetchall()
    cols = []

    for elt in cursor.description:
        cols.append(elt[0])

    df = pd.DataFrame(data=data, columns=cols)

    return df.shop_id.astype(str)
