from sqlalchemy import func

from src.database.session import db
from src.models import *


data = db.query(FacebookAd.creative, FacebookAd.image_hashes).filter(func.random() < 0.0001).limit(1000).all()

types = set([type(row.image_hashes) for row in data])
print(types)
