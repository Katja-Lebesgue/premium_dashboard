import os
import string
import sys
from io import StringIO
from dateutil.relativedelta import relativedelta

import nltk
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
from matplotlib import pyplot as plt
from nltk.tokenize.casual import TweetTokenizer
from wordcloud import WordCloud
from src.models import Crm
from src import crud
from src.models.enums.facebook import TextType
from src.models.enums import Industry

from src.database.session import db
from src.app.utils.cache_functions import st_read_csv_from_s3
from src.utils import *
from src.app.frontend_names import get_frontend_name
from src.interfaces.tab import Tab

load_dotenv()

sentiment_metrics = ("compound", "neg", "neu", "pos", "subjectivity")


@st.cache_data
def ping_text_samples(text_type: TextType, sample_size: int = 10_000, n_months: int = 3) -> pd.DataFrame:
    today = date.today()
    df = pd.DataFrame()
    for industry in list(Industry):
        industry_data = crud.fb_creative_features.get_text_sample(
            db=db,
            sample_size=sample_size,
            start_date=today - relativedelta(months=n_months),
            end_date=today,
            industry=industry,
            text_type=text_type,
        )
        industry_df = pd.DataFrame(industry_data)
        df = pd.concat([df, industry_df], axis=0)
    test_shop_ids = [shop_.id for shop_ in crud.shop.get_test_shops(db=db)]
    df = df[~df.shop_id.isin(test_shop_ids)]
    df = df.rename(columns={"industry_enum": "industry"})

    return df


class TextAnalysisTab(Tab):
    def show(self) -> None:
        col, _ = st.columns([1, 2])
        with col:
            text_type = st.selectbox(
                label="Text type", options=list(TextType), format_func=get_frontend_name, index=1
            )
        df = ping_text_samples(text_type=text_type).copy()
        sbs = get_samples_by_shop(df=df, text_type=text_type)

        st.subheader("Style")
        # wc & ec
        emoji_cloud = EmojiCloud()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#")
            st.markdown("##### All industries", unsafe_allow_html=True)
            st.markdown("######")
            display_word_and_emoji_cloud(df=sbs, text_type=text_type, _emoji_cloud=emoji_cloud)
            market_collocations = get_sorted_collocations(df=sbs, min_shops_using_phrase=5)
            st.write("Most common phrases")
            st.write(" | ".join(market_collocations))

        with col2:
            grouped_by_industry = sbs.groupby("industry")
            industry = st.selectbox(label="Choose industry", options=sorted(df.industry.unique()))
            df = grouped_by_industry.get_group(industry)
            display_word_and_emoji_cloud(df=df, text_type=text_type, _emoji_cloud=emoji_cloud)
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
            sentiment_type = st.selectbox(label="Select sentiment type", options=sentiment_metrics)
        fig = plt.figure()
        sns.boxplot(data=sbs, y="industry", x=sentiment_type, showfliers=False)
        st.pyplot(fig)

        st.markdown("#")

        st.subheader("Word count")
        fig = plt.figure()
        sns.boxplot(data=sbs, y="industry", x="word_count", showfliers=False)
        st.pyplot(fig)

        st.subheader("Text length through time")
        list_of_objects = pd.Series(list_objects_from_prefix(prefix="prljavo/text_length")).sort_values()
        text_length_df_path = list_of_objects[len(list_of_objects) - 2]
        text_length_df = st_read_csv_from_s3(text_length_df_path, add_global_folder=False)
        text_length_through_time(df=text_length_df, text_type=text_type)


@st.cache_data
def get_samples_by_shop(df: pd.DataFrame, text_type: str) -> pd.DataFrame:
    df = df[df[text_type].apply(lambda x: len(x) > 0)]
    df = df.explode(text_type).drop_duplicates(text_type)[[text_type, "industry", "shop_id"]]

    df["language"] = df[text_type].apply(lambda text: detect_language(text))
    # df = df[df.language == "en"]
    # take max 5 unique ads from shop
    df = df.groupby("shop_id").apply(lambda df: df.iloc[:30, :])

    tokenizer = TweetTokenizer()
    df["word_tokens"] = df[text_type].apply(
        lambda text: [word.lower() for word in tokenizer.tokenize(text) if word not in string.punctuation]
    )
    df["concatinated_tokens"] = df.word_tokens.apply(lambda x: " ".join(x))

    # word count and sentiment
    df["word_count"] = df.word_tokens.apply(len)
    sentiment = df[text_type].apply(lambda x: get_sentiment(x)).apply(pd.Series)
    df = df.join(sentiment)

    return df


@st.cache_data
def display_word_and_emoji_cloud(df: pd.DataFrame, text_type: str, _emoji_cloud):
    wc, ec = get_word_and_emoji_cloud(df, text_type, _emoji_cloud)
    st.write("Word cloud")
    display_cloud(wc)
    st.write("Emoji cloud")
    display_cloud(ec)


@st.cache_data
def get_word_and_emoji_cloud(df: pd.DataFrame, text_type: str, _emoji_cloud):
    full = " ".join(df[text_type].tolist())
    wc = WordCloud().generate_from_text(full)
    ec = _emoji_cloud.generate(full)
    return wc, ec


def display_cloud(wc, title: str | None = None):
    fig = plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.title(title)
    st.pyplot(fig)
    st.markdown("###")


@st.cache_data
def get_sorted_collocations(df: pd.DataFrame, min_shops_using_phrase: int = 2):
    collocations = get_collocations(df, min_shops_using_phrase)
    sorted_collocations = dict(sorted(collocations.items(), key=lambda item: item[1], reverse=True)).keys()
    return list(sorted_collocations)


@st.cache_data
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


@st.cache_data
def text_length_through_time(df: pd.DataFrame, text_type: str):
    df[text_type] = df[f"{text_type}_length"].div(df[f"{text_type}_num_shops"])

    fig = px.bar(
        df,
        x="year_month",
        y=text_type,
    )

    fig.update_layout(barmode="stack")

    st.plotly_chart(fig)


text_analysis_tab = TextAnalysisTab()
