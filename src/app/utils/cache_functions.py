import streamlit as st

from src.utils import *


@st.experimental_memo
def st_read_csv_from_s3(*args, **kwargs):
    df = read_csv_from_s3(*args, **kwargs)
    return df
