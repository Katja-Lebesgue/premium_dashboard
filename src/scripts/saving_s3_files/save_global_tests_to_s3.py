import sys

sys.path.append("././.")

from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.database.session import db
from src.scripts.saving_s3_files.save_global_creative_type_tests_to_s3 import (
    save_global_creative_type_tests_to_s3,
)
from src.scripts.saving_s3_files.save_global_descriptive_statistics_to_s3 import (
    save_global_descriptive_statistics_to_s3,
)
from src.scripts.saving_s3_files.save_global_feature_tests_to_s3 import save_global_feature_tests_to_s3
from src.scripts.saving_s3_files.save_global_promotion_tests_to_s3 import save_global_promotion_tests_to_s3
from src.utils import *


@print_execution_time
def main():
    start_dates = []

    end_date = date.today().strftime("%Y-%m-%d")

    end_date = "2023-06-01"

    for months in [3, 6, 12]:
        end_date_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_dates.append(datetime.strftime((end_date_date - relativedelta(months=months)), "%Y-%m-%d"))

    print(f"start_dates: {start_dates}")

    for start_date in start_dates:
        print(f"saving promotion from {start_date}")
        save_global_promotion_tests_to_s3(db=db, start_date=start_date, end_date=end_date)

        print(f"saving features from {start_date}")
        save_global_feature_tests_to_s3(db=db, start_date=start_date, end_date=end_date)

        print(f"saving creative from {start_date}")
        save_global_creative_type_tests_to_s3(db=db, start_date=start_date, end_date=end_date)

    print(f"saving description")
    # save_global_descriptive_statistics_to_s3(end_date=end_date)


if __name__ == "__main__":
    main()
