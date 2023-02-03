import sys

sys.path.append("./.")

import sqlalchemy.orm.relationships

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import Session
from src.pingers import *
from src.models import *
from src.database.session import db

import streamlit as st


def select_shop_and_load_data() -> pd.DataFrame:

    shops = st_get_shops()

    shops = shops.sort_values("name").reset_index()

    shops_dict = shops.set_index("shop_id").to_dict()["name"]

    shop_index = int(shops[shops.shop_id == "16038"].index[0])

    st.write(shop_index)

    selected_shop_id = st.selectbox(
        "Select shop",
        options=shops["shop_id"],
        format_func=lambda x: shops_dict[x],
        index=shop_index,
    )

    st.write(f"shop id: {selected_shop_id}")

    data_shop = st_get_data_by_shop_id(selected_shop_id)
    data_shop_copy = data_shop.copy()

    return data_shop_copy


@st.cache
def st_get_shops() -> pd.Series:
    # return ["2"]
    print("st_select_ids")
    shops = ping_shops(db=db)
    return shops


@st.experimental_memo
def st_get_data_by_shop_id(shop_id) -> pd.DataFrame:
    print("st_select_shop")
    df = ping_creative_and_performance(shop_id=shop_id)
    df["count"] = 1
    return df
