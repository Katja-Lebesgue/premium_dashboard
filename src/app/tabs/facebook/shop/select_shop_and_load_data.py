import sys

sys.path.append("./.")

import pandas as pd
import sqlalchemy.orm.relationships
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from loguru import logger
from sqlalchemy.orm import Session

from src.app.authenticate import is_admin
from src.crud import crud_streamlit_user_shop
from src.database.session import SessionLocal
from src.models import *
from src.pingers import *

db = SessionLocal()


def select_shop_and_load_data() -> pd.DataFrame:
    
    if not is_admin():
        shops = crud_streamlit_user_shop.ping_shops_by_streamlit_user_id(
            db=db, streamlit_user_id=st.session_state["user_id"]
        ).rename(columns={"id": "shop_id"})
    else:
        shops = st_get_shops()

    shops = shops.sort_values("name").reset_index()

    if not len(shops):
        return pd.DataFrame()

    selected_shop_id = st.selectbox(
        "Select shop",
        options=shops["shop_id"],
        format_func=lambda shop_id: shops.loc[shops.shop_id == shop_id, "name"].item(),
    )

    data_shop = st_get_data_by_shop_id(selected_shop_id)
    data_shop_copy = data_shop.copy()

    return data_shop_copy


@st.experimental_memo
def st_get_shops() -> pd.Series:
    print("st_select_ids")
    shops = ping_shops(db=db)
    return shops


@st.experimental_memo
def st_get_data_by_shop_id(shop_id) -> pd.DataFrame:
    print("st_select_shop")
    df = ping_creative_and_performance(db=db, shop_id=shop_id)
    df["count"] = 1
    return df
