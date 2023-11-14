import streamlit as st

from src.abc.descriptive import *
from src.abc.descriptive import DescriptiveDF
from src.app.frontend_names import get_frontend_name
from src.app.tabs.descriptive_tab.descriptive_tab import DescriptiveTab, metrics
from src.utils import *


class MarketDescriptiveTab(DescriptiveTab):
    analysis_type_help = (
        "Select which kind of analysis you want to see. This select box changes the content"
        " of the whole page (including time graph). If you select _total_, you will see sum"
        " of all metrics in the selected period, i.e. total spend of all Lebesgue shops in"
        " June 2023, and if you select _by shop_, the number displayed will"
        " correspond to the average metric by shop, i.e. how much an average shop spent in"
        " June 2023."
    )

    def show(self):
        summary_df = self.get_most_recent_df(cache_id=type(self).__name__, df_type=DescriptiveDF.summary)

        col1, _ = st.columns([1, 2])
        with col1:
            analysis_type = st.selectbox(
                label="Analysis type",
                options=("total", "by shop"),
                help=self.analysis_type_help,
            )

        if analysis_type == "by shop":
            summary_df = summary_df.drop(columns=self.metric_columns)
            summary_df = summary_df.rename(columns={col + "_by_shop": col for col in self.metric_columns})
            pie_func = "mean"
        else:
            pie_func = "sum"

        self.pie_charts(
            summary_df=summary_df.copy(),
            add_title=(analysis_type == "total"),
            func=pie_func,
        )
        self.descriptive_features_through_time(
            summary_df=summary_df, show_relative_option=(analysis_type == "total")
        )

        main_df = self.get_most_recent_df(cache_id=type(self).__name__, df_type=DescriptiveDF.main)
        main_df = main_df[main_df.spend_USD > main_df.spend_USD.quantile(0.25)]
        self.benchmarks(main_df=main_df)

    @property
    def available_metrics(self):
        return self.metric_columns + ["n_shops"]

    @st.cache_data
    def get_most_recent_df(_self, cache_id: str, df_type: DescriptiveDF):
        end_date = max(_self.get_available_dates(df_type=df_type))
        main_df = _self.read_df(df_type=df_type, end_date=end_date)
        main_df["year_month"] = main_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))
        main_df["feature_value"] = main_df.feature_value.apply(get_frontend_name)
        for metric in metrics:
            main_df[str(metric)] = main_df.apply(metric.formula_series, axis=1)
        return main_df


class FacebookCreativeMarketDescriptiveTab(MarketDescriptiveTab, FacebookCreativeDescriptive):
    ...


class FacebookTargetMarketDescriptiveTab(MarketDescriptiveTab, FacebookTargetDescriptive):
    ...


class FacebookImageMarketDescriptiveTab(MarketDescriptiveTab, FacebookImageDescriptive):
    def show(self):
        with (col := st.columns([1, 1])[0]):
            st.info(
                f"This analysis includes only images corresponding to top {FacebookImageDescriptive.n_ads_per_shop_and_month} image ads by spend for each shop and month."
            )
        super().show()


class GoogleCampaignTypeMarketDescriptiveTab(MarketDescriptiveTab, GoogleCampaignTypeDescriptive):
    ...


facebook_creative_market_descriptive_tab = FacebookCreativeMarketDescriptiveTab()
facebook_target_market_descriptive_tab = FacebookTargetMarketDescriptiveTab()
facebook_image_market_descriptive_tab = FacebookImageMarketDescriptiveTab()
google_campaign_type_market_descriptive_tab = GoogleCampaignTypeMarketDescriptiveTab()
