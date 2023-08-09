import sys

sys.path.append("./.")

import pandas as pd
from tqdm import tqdm

from src.database.inserters_and_updaters.upsert_creative_by_shop_id import upsert_creative_by_shop_id
from src.database.queries.query_shop_id import query_shop_id
from src.database.session import SessionLocal
from src.utils import read_csv_and_eval
from utils.timing import print_execution_time


@print_execution_time
def main():
    session = SessionLocal()
    print("pinging shop ids...")
    query = query_shop_id(session=session, start_date="2022-05-01")
    shop_ids = pd.read_sql(query.statement, session.bind)["shop_id"]
    print("finished.")

    update_df_path = "data/creative_update_metadata.csv"

    update_df = read_csv_and_eval(update_df_path).set_index(["shop_id"])

    print(update_df)

    for shop_id in tqdm(shop_ids, total=len(shop_ids)):
        print(f"updating shop id {shop_id}...")
        try:
            update_df, success = upsert_creative_by_shop_id(
                shop_id=shop_id, update_df=update_df, end_date="2023-08-08"
            )

            if success:
                update_df.to_csv(update_df_path)
        except:
            print(f"nije uspjelo za shop id {shop_id}")
            pass


if __name__ == "__main__":
    main()
