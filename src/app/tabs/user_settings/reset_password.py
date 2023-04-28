import streamlit as st
import yaml
from streamlit_option_menu import option_menu

from src.crud.streamlit import crud_streamlit_user
from src.database.session import db


def reset_password(authenticator):
    with st.sidebar:
        subtab = option_menu(
            menu_title="Settings",
            options=["Change password"],
            menu_icon="gear",
            icons=["hash"],
            default_index=0,
        )

    if subtab == "Change password":
        try:
            if authenticator.reset_password(st.session_state["username"], "Reset password"):
                st.success("Password modified successfully")
                new_hashed_password = authenticator.credentials["usernames"][st.session_state["username"]][
                    "password"
                ].encode()
                crud_streamlit_user.update_hashed_password(
                    db=db, id=st.session_state["user_id"], hashed_password=new_hashed_password
                )
        except Exception as e:
            st.error(e)
