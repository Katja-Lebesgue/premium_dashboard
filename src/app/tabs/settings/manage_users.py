from time import sleep

import pandas as pd
import streamlit as st
from sqlalchemy.exc import IntegrityError

from src import crud
from src.database.session import db
from src.utils import *


def manage_users():
    users = crud.streamlit_user.get_all_subusers(db=db)
    user_id_name_dict = {user.id: user.username for user in users}

    # register user
    reg_user_form = st.form("Register user")
    reg_user_form.subheader("Register user")
    new_username = reg_user_form.text_input("Username").lower()
    new_password = reg_user_form.text_input("Password", type="password")
    new_password_repeat = reg_user_form.text_input("Repeat password", type="password")

    if reg_user_form.form_submit_button("Register"):
        try:
            if new_password == new_password_repeat:
                hashed_password = hash_password(new_password)
                crud.streamlit_user.add_user(db=db, username=new_username, hashed_password=hashed_password)
                st.experimental_rerun()

            else:
                st.error("Passwords do not match.")
        except IntegrityError:
            st.error("Username already exists.")
            db.rollback()

    # delete user
    delete_user_form = st.form("Delete user")
    delete_user_form.subheader("Delete user")
    user_id = delete_user_form.selectbox(
        label="Select user",
        options=user_id_name_dict.keys(),
        format_func=lambda id: user_id_name_dict[id],
    )

    if delete_user_form.form_submit_button("Delete"):
        crud.streamlit_user.delete_user(db=db, id=user_id)
        st.experimental_rerun()

    # reset password
    reset_password_form = st.form("Reset password")
    reset_password_form.subheader("Reset password")
    user_id = reset_password_form.selectbox(
        label="Select user",
        options=user_id_name_dict.keys(),
        format_func=lambda id: user_id_name_dict[id],
    )
    new_password = reset_password_form.text_input("Password", type="password")
    new_password_repeat = reset_password_form.text_input("Repeat password", type="password")

    if reset_password_form.form_submit_button("Reset"):
        if new_password == new_password_repeat:
            crud.streamlit_user.update_hashed_password(
                db=db, id=user_id, hashed_password=hash_password(new_password)
            )
            st.success("Password modified successfully.")

        else:
            st.error("Passwords do not match.")
