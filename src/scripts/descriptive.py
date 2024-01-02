import sys

sys.path.append("./.")

from argparse import ArgumentParser
from datetime import date

from src.database.session import db
from src.interfaces.descriptive import *
from src.utils import *

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-f", "--force_from_scratch", action="store_true", default=False)
    parser.add_argument("-t", "--testing", action="store_true", default=False)
    args = parser.parse_args()

    facebook_creative_descriptive.save_for_all_shops(
        db=db, force_from_scratch=args.force_from_scratch, testing=args.testing
    )
    facebook_creative_descriptive.create_and_save_summary()

    facebook_target_descriptive.save_for_all_shops(
        db=db, force_from_scratch=args.force_from_scratch, testing=args.testing
    )
    facebook_target_descriptive.create_and_save_summary()

    google_campaign_type_descriptive.save_for_all_shops(
        db=db, force_from_scratch=args.force_from_scratch, testing=args.testing
    )
    google_campaign_type_descriptive.create_and_save_summary()

    # facebook_image_descriptive.save_everything(force_from_scratch=args.force_from_scratch)
