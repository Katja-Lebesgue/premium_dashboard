import streamlit as st

from src import crud
from src.app.authenticate import is_admin
from src.database.session import db


def select_shop() -> int:
    shops_dict = get_nontest_shop_dict(admin=is_admin(), user_id=st.session_state.get("user_id"))

    if not len(shops_dict):
        st.warning("You don't have permission to see data for any shop!")

    fewmoda_index = list(shops_dict.keys()).index(16038)

    selected_shop_id = st.selectbox(
        "Select shop",
        options=shops_dict.keys(),
        format_func=lambda shop_id: shops_dict[shop_id],
        index=fewmoda_index,
    )

    return selected_shop_id


@st.cache_data
def get_nontest_shop_dict(user_id: int, admin: bool = False):
    if not admin:
        shops = crud.streamlit_user_shop.get_shops_by_streamlit_user_id(db=db, streamlit_user_id=user_id)
    else:
        shops = crud.shop.get_nontest_shops(db=db)

    shops_dict = {shop_.id: shop_.name for shop_ in shops}
    return dict(sorted(shops_dict.items(), key=lambda x: x[1]))
