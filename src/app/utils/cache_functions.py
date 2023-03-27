import streamlit as st

from src.s3.read_file_from_s3 import read_csv_from_s3


@st.experimental_memo
def st_read_csv_from_s3(*args, **kwargs):
    df = read_csv_from_s3(*args, **kwargs)
    return df
