import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

import nltk

nltk.download("vader_lexicon")
nltk.download("stopwords")


from src.app import *
from src.app.authenticate import authenticate

st.set_page_config(layout="wide")

pd.set_option("mode.chained_assignment", None)

authenticator = authenticate()

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    get_main_menu().show(authenticator=authenticator)
