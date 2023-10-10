from src import crud
from src.database.session import db
from src.pingers import *
from src.services import facebook_image_descriptive_saver as fi

shop_id = 16038

df = fi.create_and_save_main(db=db, force_from_scratch=True, testing=True)
