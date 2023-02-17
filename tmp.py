from src.database.session import db
from src.scripts.saving_s3_files.save_global_descriptive_statistics_to_s3 import (
    save_global_descriptive_statistics_to_s3,
)


if __name__ == "__main__":
    save_global_descriptive_statistics_to_s3(db=db, force_from_scratch=True)
