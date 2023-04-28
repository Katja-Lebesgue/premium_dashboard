import os

import bcrypt
from dotenv import load_dotenv

load_dotenv()

salt = os.getenv("SALT").encode()


def hash_password(password: str):
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password
