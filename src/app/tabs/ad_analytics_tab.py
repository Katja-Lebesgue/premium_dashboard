import webbrowser

from datetime import timedelta
import streamlit as st
import streamlit.components.v1 as components
from dateutil.relativedelta import relativedelta
from streamlit.components.v1 import html
from streamlit_modal import Modal

from src import crud
from src.app.frontend_names import get_frontend_name, n_days_to_period
from src.app.utils import *
from src.app.utils import filter_df
from src.database.session import db
from src.fb_api.get_preview_shareable_link import get_preview_shareable_link
from src.models import Shop
from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES, TARGET_FEATURES, TextFeature, TextType
from src.pingers import ping_facebook_creative_target_and_performance
from src.utils import *

metrics = (cac, ctr, cr, cpm)
descriptive_columns = ["spend_USD", "impr", "purch", "purch_value_USD", "clicks"]

ad_feature_columns = ["ad_id", "name", "creative_type", "target", "audience"]


def get_ads_data(shop_id: int) -> pd.DataFrame:
    shop_df = ping_facebook_creative_target_and_performance(
        db=db,
        shop_id=shop_id,
        enum_to_value=True,
        period=Period.date,
        start_date=date.today() - relativedelta(years=1),
    )
    ad_names = crud.fb_ad.get_names(db=db, shop_id=shop_id)
    ad_names_df = pd.DataFrame([row._asdict() for row in ad_names])
    shop_df = shop_df.merge(ad_names_df, on=["ad_id", "account_id"])
    return shop_df


def open_page(url):
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (
        url
    )
    html(open_script)


def ad_analytics_tab(shop_id: int):
    shop_df = st_cache_data(
        _func=get_ads_data,
        func_name=get_ads_data.__name__,
        shop_id=shop_id,
    )

    if len(shop_df) == 0:
        st.warning("No data.")
        return

    date_presets_column, date_slider_columm = st.columns([1, 2])

    with date_presets_column:
        days_in_past = st.radio(
            label="Date presets:",
            options=[7, 14, 30, 90, 365],
            format_func=lambda n_days: f"Last {n_days_to_period(n_days)}",
        )
        default_min_date = shop_df.date.max() - timedelta(days=days_in_past)

    with date_slider_columm:
        shop_df = filter_df(
            df=shop_df,
            column_name="date",
            filter_type=FilterType.slider,
            slider_default_lower_bound=default_min_date,
            format_func=lambda dt: dt.strftime("%y-%m-%d"),
        )

    if not len(shop_df):
        st.warning("Empty dataframe!")
        return

    aggregated_metrics = shop_df.groupby(["ad_id", "account_id"])[descriptive_columns].sum()

    shop_df = aggregated_metrics.merge(
        shop_df[
            ["ad_id", "account_id", "creative_type", "name"]
            + BOOLEAN_TEXT_FEATURES
            + TARGET_FEATURES
            + get_enum_values(TextType)
        ],
        on=["ad_id", "account_id"],
    ).drop_duplicates(["ad_id", "account_id"])

    for metric in metrics:
        shop_df[str(metric)] = shop_df.apply(metric.formula_series, axis=1)

    col1, col2, col3 = st.columns(3)

    with col1:
        shop_df = filter_df(df=shop_df, column_name="audience", filter_type=FilterType.checkbox)
    with col2:
        shop_df = filter_df(df=shop_df, column_name="creative_type", filter_type=FilterType.checkbox)
    with col3:
        shop_df = filter_df(df=shop_df, column_name=TextFeature.discount, filter_type=FilterType.checkbox)

    if not len(shop_df):
        st.warning("Empty dataframe!")
        return

    col4, col5 = st.columns([1, 2])

    shop_df = shop_df[
        (shop_df.spend_USD.notna())
        & (shop_df[str(cac)].notna())
        & (shop_df[str(cpm)].notna())
        & (shop_df[str(ctr)].notna())
    ]

    with col4:
        with st.expander("Filter by metric"):
            shop_df = filter_df(
                df=shop_df,
                column_name="spend_USD",
                filter_type=FilterType.slider,
                format_func=lambda num: f"${big_number_human_format(num)}",
            )
            shop_df = filter_df(
                df=shop_df,
                column_name=str(cac),
                filter_type=FilterType.slider,
                format_func=lambda num: f"${big_number_human_format(num)}",
            )
            shop_df = filter_df(
                df=shop_df,
                column_name=str(cpm),
                filter_type=FilterType.slider,
                format_func=lambda num: f"${big_number_human_format(num)}",
            )
            shop_df = filter_df(
                df=shop_df,
                column_name=str(ctr),
                filter_type=FilterType.slider,
                format_func=lambda num: f"{big_number_human_format(num, small_decimals=2)}%",
            )

    if not len(shop_df):
        st.warning("Empty dataframe!")
        return

    with col5:
        with st.expander("Select columns"):
            (
                ad_features_st_col,
                descriptive_st_col,
                metrics_st_column,
                texts_st_col,
            ) = st.columns(4)
            selected_columns = []
            with ad_features_st_col:
                st.write("Ad features")
                selected_columns.extend(
                    checkbox_menu(
                        labels=ad_feature_columns, true_labels=["name", "creative_type"], key="ad_features"
                    )
                )

            with descriptive_st_col:
                st.write("Descriptive columns")
                selected_columns.extend(
                    checkbox_menu(labels=descriptive_columns, true_labels=["spend_USD"], key="descriptive")
                )
            with metrics_st_column:
                st.write("Metrics")
                selected_columns.extend(checkbox_menu(labels=list(map(str, metrics)), key="metrics"))

            with texts_st_col:
                st.write("Ad copy")
                selected_columns.extend(
                    checkbox_menu(labels=get_enum_values(TextType), true_labels=[TextType.primary])
                )

    shop_df[descriptive_columns + list(map(str, metrics))] = shop_df[
        descriptive_columns + list(map(str, metrics))
    ].applymap(lambda num: round(num, ndigits=2))

    st.dataframe(style_df(shop_df, selected_columns), height=300)
    open_download_modal = st.button("Export as CSV")

    download_modal = Modal("Export as CSV", key="hop", padding=20, max_width=710)
    if open_download_modal:
        download_modal.open()

    if download_modal.is_open():
        with download_modal.container():
            order_by_st_column, top_n_st_column = st.columns([1, 1])
            with order_by_st_column:
                order_column = st.selectbox(
                    label="Order by",
                    options=(str(cac), str(cpm), str(ctr), str(cr), "spend_USD"),
                    format_func=get_frontend_name,
                )
                ascending = st.checkbox(label="Ascending", value=True)
                shop_df = shop_df.sort_values(order_column, ascending=ascending)
            with top_n_st_column:
                n_ads = st.number_input(min_value=1, max_value=20, label="Number of top rows", value=5)
                shop_df = shop_df.head(n_ads)
                add_links_st_col, open_links_st_col = st.columns(2)
                with add_links_st_col:
                    add_links_button = st.button("Add preview links")
                if add_links_button:
                    if "preview_link" not in shop_df.columns:
                        add_preview_links_to_df(df=shop_df, shop_id=shop_id)
                        selected_columns.append("preview_link")
                with open_links_st_col:
                    open_links_button = st.button("Open preview links")
                    if open_links_button:
                        if "preview_link" not in shop_df.columns:
                            add_preview_links_to_df(df=shop_df, shop_id=shop_id)
                            selected_columns.append("preview_link")
            shop_name = db.query(Shop.name).filter(Shop.id == shop_id).first().name
            file_name = st.text_input(label="File name", value=f"top_{n_ads}_ads_for_{shop_name}.csv")
            st.dataframe(style_df(shop_df, selected_columns), height=180)
            st.download_button(
                label="Download",
                data=shop_df[selected_columns].to_csv(index=False).encode("utf-8"),
                file_name=file_name,
            )
            if open_links_button:
                for preview_link in shop_df.preview_link:
                    open_page(preview_link)


def add_preview_links_to_df(df: pd.DataFrame, shop_id: int):
    access_token = crud.credentials.get_facebook_access_token_by_shop(db=db, shop_id=shop_id)
    df["preview_link"] = df.ad_id.apply(
        lambda ad_id: get_preview_shareable_link(ad_id=ad_id, access_token=access_token)
    )

    return df


def style_df(df: pd.DataFrame, selected_columns: list[str]):
    return df[selected_columns].style.format(
        formatter=lambda num: big_number_human_format(num=num, small_decimals=2),
        subset=list(set(selected_columns).intersection(descriptive_columns + list(map(str, metrics)))),
    )
