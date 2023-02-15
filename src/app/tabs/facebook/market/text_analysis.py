import streamlit as st
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from dotenv import load_dotenv
import os
import pandas as pd

from src.s3.read_file_from_s3 import read_csv_from_s3
from src.utils.nlp import EmojiCloud
from src.feature_extractors.EText import EText
from src.utils.enum import get_enum_values

load_dotenv()


@st.cache(allow_output_mutation=True)
def get_word_and_emoji_cloud(df: pd.DataFrame, text_col: str, emoji_cloud):
    full = " ".join(df[f"concatinated_{text_col}"].tolist())
    wc = WordCloud().generate_from_text(full)
    ec = emoji_cloud.generate(full)
    return wc, ec


def display_cloud(wc, title: str | None = None):
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(wc)
    plt.axis("off")
    plt.title(title)
    st.pyplot(fig)


def text_analysis():
    df = read_csv_from_s3("global/data/texts_2022.csv")
    text_col = st.selectbox(label="Text position", options=get_enum_values(EText))
    df = df[df[text_col].apply(lambda x: len(x) > 0)]
    df[f"concatinated_{text_col}"] = df[text_col].apply(lambda x: " ".join(x))
    samples_by_shop = df.groupby("shop_id").sample(30, replace=True).drop_duplicates(subset=f"concatinated_{text_col}")
    full = " ".join(samples_by_shop[f"concatinated_{text_col}"].tolist())
    emoji_cloud = EmojiCloud(font_path=f"{os.getenv('GLOBAL_PATH_TO_REPO')}/data/Symbola.otf")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("All industries")
        wc, ec = get_word_and_emoji_cloud(df, text_col, emoji_cloud)
        display_cloud(wc)
        display_cloud(ec)

    with col2:
        grouped_by_industry = samples_by_shop.groupby("industry")
        industry = st.selectbox(label="Industry", options=df.industry.unique())
        df = grouped_by_industry.get_group(industry)
        wc, ec = get_word_and_emoji_cloud(df, text_col, emoji_cloud)
        display_cloud(wc)
        display_cloud(ec)
