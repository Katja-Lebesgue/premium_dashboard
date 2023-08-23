import sys

sys.path.append("./.")

from datetime import date

from argparse import ArgumentParser

from src.utils import *
from src.database.session import db
from src.services.descriptive_saver import (
    facebook_creative_descriptive_saver,
    facebook_target_descriptive_saver,
    google_campaign_type_descriptive_saver,
)

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-d", "--end_date", default=str(date.today()))
    parser.add_argument("-f", "--force_from_scratch", action="store_true", default=False)
    args = parser.parse_args()
    end_date = to_date(args.end_date)
    last_day_of_previous_month = get_last_day_of_the_previous_month(end_date)

    # facebook_creative_descriptive_saver.create_and_save_main(
    #     db=db, end_date=end_date, force_from_scratch=args.force_from_scratch
    # )

    # facebook_target_descriptive_saver.create_and_save_main(
    #     db=db, end_date=end_date, force_from_scratch=args.force_from_scratch
    # )

    # google_campaign_type_descriptive_saver.create_and_save_main(
    #     db=db, end_date=end_date, force_from_scratch=args.force_from_scratch
    # )

    facebook_creative_descriptive_saver.create_and_save_summary(end_date=last_day_of_previous_month)
    facebook_target_descriptive_saver.create_and_save_summary(end_date=last_day_of_previous_month)
    google_campaign_type_descriptive_saver.create_and_save_summary(end_date=last_day_of_previous_month)
