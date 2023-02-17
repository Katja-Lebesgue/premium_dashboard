import streamlit as st
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO
import sys
import nltk
from nltk.tokenize.casual import TweetTokenizer
import string
from loguru import logger
import seaborn as sns

from src.s3.read_file_from_s3 import read_csv_from_s3
from src.utils.nlp import EmojiCloud
from src.feature_extractors.EText import EText
from src.utils.enum import get_enum_values
from src.utils.nlp import get_sentiment

load_dotenv()


def text_analysis():
    df = st_get_text_data()
    df = df.copy()
    col, _ = st.columns([1, 2])
    with col:
        text_col = st.selectbox(label="Text position", options=get_enum_values(EText))
    sbs, sentiment_columns = get_samples_by_shop(df=df, text_col=text_col)

    st.subheader("Style")
    # wc & ec
    emoji_cloud = EmojiCloud(font_path=f"{os.getenv('GLOBAL_PATH_TO_REPO')}/data/Symbola.otf")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#")
        st.markdown("##### All industries", unsafe_allow_html=True)
        st.markdown("######")
        display_word_and_emoji_cloud(df=sbs, text_col=text_col, emoji_cloud=emoji_cloud)
        market_collocations = get_sorted_collocations(df=sbs, min_shops_using_phrase=5)
        st.write("Most common phrases")
        st.write(" | ".join(market_collocations))

    with col2:
        grouped_by_industry = sbs.groupby("industry")
        industry = st.selectbox(label="Choose industry", options=sorted(df.industry.unique()))
        df = grouped_by_industry.get_group(industry)
        display_word_and_emoji_cloud(df=df, text_col=text_col, emoji_cloud=emoji_cloud)
        collocations = get_sorted_collocations(df=df, min_shops_using_phrase=2)
        st.write("Most common phrases")
        collocations_md = ""
        for i, phrase in enumerate(collocations):
            if phrase in market_collocations:
                phrase_md = phrase
            else:
                phrase_md = f"<span style='color:red; font-weight:bold'>{phrase}</span>"
            if i == 0:
                collocations_md = phrase_md
            else:
                collocations_md = collocations_md + " | " + phrase_md
        st.markdown(collocations_md, unsafe_allow_html=True)

    st.subheader("Sentiment")
    col1, _ = st.columns([1, 3])
    with col1:
        sentiment_type = st.selectbox(label="Select sentiment type", options=sentiment_columns)
    fig = plt.figure()
    sns.boxplot(data=sbs, y="industry", x=sentiment_type, showfliers=False)
    st.pyplot(fig)

    st.markdown("#")

    st.subheader("Word count")
    fig = plt.figure()
    sns.boxplot(data=sbs, y="industry", x="word_count", showfliers=False)
    st.pyplot(fig)


@st.experimental_memo
def st_get_text_data():
    df = read_csv_from_s3("global/data/texts_2022.csv")
    return df


@st.experimental_memo
def get_samples_by_shop(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    df = df[df[text_col].apply(lambda x: len(x) > 0)]
    df[f"concatinated_{text_col}"] = df[text_col].apply(lambda x: " ".join(x))

    sbs = df.groupby("shop_id").sample(30, replace=True).drop_duplicates(subset=f"concatinated_{text_col}")

    tokenizer = TweetTokenizer()
    sbs["word_tokens"] = sbs[text_col].apply(
        lambda x: [word.lower() for word in tokenizer.tokenize(x[0]) if word not in string.punctuation]
    )
    sbs["concatinated_tokens"] = sbs.word_tokens.apply(lambda x: " ".join(x))

    # remove lebesgue ads
    lebesgue_shop_ids = sbs.loc[sbs.word_tokens.apply(lambda tokens: "lebesgue" in tokens), "shop_id"].unique()
    sbs = sbs[~sbs.shop_id.isin(lebesgue_shop_ids)]

    # word count and sentiment
    sbs["word_count"] = sbs.word_tokens.apply(len)
    sentiment = sbs[text_col].apply(lambda x: get_sentiment(x[0])).apply(pd.Series)
    sbs = sbs.join(sentiment)

    return sbs, sentiment.columns


def display_word_and_emoji_cloud(df: pd.DataFrame, text_col: str, emoji_cloud):
    wc, ec = get_word_and_emoji_cloud(df, text_col, emoji_cloud)
    st.write("Word cloud")
    display_cloud(wc)
    st.write("Emoji cloud")
    display_cloud(ec)


@st.cache(allow_output_mutation=True)
def get_word_and_emoji_cloud(df: pd.DataFrame, text_col: str, emoji_cloud):
    full = " ".join(df[f"concatinated_{text_col}"].tolist())
    wc = WordCloud().generate_from_text(full)
    ec = emoji_cloud.generate(full)
    logger.debug("Opet wc!")
    return wc, ec


def display_cloud(wc, title: str | None = None):
    fig = plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.title(title)
    st.pyplot(fig)
    st.markdown("###")


def get_sorted_collocations(df: pd.DataFrame, min_shops_using_phrase: int = 2):
    collocations = get_collocations(df, min_shops_using_phrase)
    sorted_collocations = dict(sorted(collocations.items(), key=lambda item: item[1], reverse=True)).keys()
    return sorted_collocations


@st.experimental_memo
def get_collocations(df: pd.DataFrame, min_shops_using_phrase: int = 1):
    all_word_tokens = sum(df.word_tokens.tolist(), [])
    all_word_tokens = [token for token in all_word_tokens if "_" not in token]
    text = nltk.Text(all_word_tokens, [])
    old_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout
    text.collocations()
    collocations = new_stdout.getvalue()
    sys.stdout = old_stdout
    collocations = collocations.replace("\n", " ").split("; ")
    collocations_dict = {
        phrase: df.loc[df.concatinated_tokens.apply(lambda x: phrase in x), "shop_id"].nunique()
        for phrase in collocations
    }
    collocations_dict = {k: v for k, v in collocations_dict.items() if v >= min_shops_using_phrase}
    return collocations_dict
