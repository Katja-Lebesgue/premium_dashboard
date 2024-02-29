import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.database.session import db

load_dotenv()

import nltk

nltk.download("vader_lexicon")
nltk.download("stopwords")


from src.app import *
from src.app.authenticate import authenticate

# with open("a.txt", "rb") as f:
# with open(f'{os.getenv("GLOBAL_PATH_TO_REPO")}/a.otf', "rb") as f:
#     a = f.read()
#     logger.success("JUPI!!!")

st.set_page_config(layout="wide")

pd.set_option("mode.chained_assignment", None)

authenticator = authenticate()

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    with st.sidebar:
        clear_cache_and_rerun_button = st.button("Reset")
        if clear_cache_and_rerun_button:
            st.experimental_memo.clear()
            st.rerun()
    get_main_menu().show(authenticator=authenticator)

db.close()
