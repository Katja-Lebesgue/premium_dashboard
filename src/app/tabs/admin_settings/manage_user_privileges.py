import pandas as pd
import streamlit as st

from src import crud
from src.database.session import db
from src.pingers import ping_shops


def manage_user_privileges():
    users = crud.streamlit_user.ping_all_subusernames(db=db)
    shops = st_ping_shops()
    user_id = st.selectbox(
        label="Select user",
        options=users["id"],
        format_func=lambda x: users.loc[users.id == x, "username"].item(),
    )

    user_shops = crud.streamlit_user_shop.ping_shops_by_streamlit_user_id(db=db, streamlit_user_id=user_id)
    forbidden_shops = shops[~shops.id.isin(user_shops.id)]

    # add shop
    add_shop_form = st.form("Add shop")
    add_shop_form.subheader("Add shop")

    shop_id = add_shop_form.selectbox(
        label="Select shop",
        options=forbidden_shops["id"],
        format_func=lambda x: forbidden_shops.loc[forbidden_shops.id == x, "name"].item(),
    )

    if add_shop_form.form_submit_button("Add"):
        crud.streamlit_user_shop.add_relationship(db=db, streamlit_user_id=user_id, shop_id=shop_id)
        st.experimental_rerun()

    # remove shop
    remove_shop_form = st.form("Remove shop")
    remove_shop_form.subheader("Remove shop")
    shop_id = remove_shop_form.selectbox(
        label="Select shop",
        options=user_shops["id"],
        format_func=lambda x: user_shops.loc[user_shops.id == x, "name"].item(),
    )

    remove_shop_button = remove_shop_form.form_submit_button("Remove")

    if remove_shop_button:
        crud.streamlit_user_shop.delete_relationship(db=db, streamlit_user_id=user_id, shop_id=shop_id)
        st.experimental_rerun()


@st.experimental_memo
def st_ping_shops():
    return crud.shop.ping_all(db=db)
