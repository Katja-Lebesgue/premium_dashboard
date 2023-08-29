import streamlit as st
from src.utils import *


@st.cache_data
def st_read_csv_from_s3(*args, **kwargs):
    df = read_csv_from_s3(*args, **kwargs)
    return df
