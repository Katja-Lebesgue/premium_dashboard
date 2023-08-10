from src import crud
from src.database.session import SessionLocal

db = SessionLocal()

relevant_shop_ids = [16038, 268714, 44301396, 2058949, 29851960, 37135321]
relevant_shops = [crud.shop.get(db=db, id=id) for id in relevant_shop_ids]
