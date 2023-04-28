from src.s3 import *
from src.database.session import db


if __name__ == "__main__":
    s3_image.save_urls_and_performance_to_s3(db=db, force_from_scratch=False)
