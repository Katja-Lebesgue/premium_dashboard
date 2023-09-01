import pandas as pd
import streamlit as st

from src import crud
from src.database.session import db
from src.pingers import ping_shops


def manage_user_privileges():
    users = crud.streamlit_user.get_all_subusers(db=db)
    user_id_name_dict = {user.id: user.username for user in users}
    all_shops = crud.shop.get_nontest_shops(db=db)
    shop_id_name_dict = {shop_.id: shop_.name for shop_ in all_shops}
    user_id = st.selectbox(
        label="Select user",
        options=user_id_name_dict.keys(),
        format_func=lambda id: user_id_name_dict[id],
    )

    user_shops = crud.streamlit_user_shop.get_shops_by_streamlit_user_id(db=db, streamlit_user_id=user_id)
    forbidden_shops = [
        shop_ for shop_ in all_shops if shop_.id not in set([user_shop.id for user_shop in user_shops])
    ]

    # add shop
    add_shop_form = st.form("Add shop")
    add_shop_form.subheader("Add shop")

    shop_id = add_shop_form.selectbox(
        label="Select shop",
        options=[shop_.id for shop_ in forbidden_shops],
        format_func=lambda id: shop_id_name_dict[id],
    )

    if add_shop_form.form_submit_button("Add"):
        crud.streamlit_user_shop.add_relationship(db=db, streamlit_user_id=user_id, shop_id=shop_id)
        st.experimental_rerun()

    # remove shop
    remove_shop_form = st.form("Remove shop")
    remove_shop_form.subheader("Remove shop")
    shop_id = remove_shop_form.selectbox(
        label="Select shop",
        options=[shop_.id for shop_ in user_shops],
        format_func=lambda id: shop_id_name_dict[id],
    )

    remove_shop_button = remove_shop_form.form_submit_button("Remove")

    if remove_shop_button:
        crud.streamlit_user_shop.delete_relationship(db=db, streamlit_user_id=user_id, shop_id=shop_id)
        st.experimental_rerun()


@st.cache_data
def st_ping_shops():
    return crud.shop.ping_all(db=db)
