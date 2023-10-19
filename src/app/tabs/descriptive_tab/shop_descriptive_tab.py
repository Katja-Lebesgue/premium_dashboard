import streamlit as st

from src.abc.descriptive import *
from src.app.frontend_names import get_frontend_name
from src.app.tabs.descriptive_tab.descriptive_tab import DescriptiveTab, metrics
from src.utils import *

analysis_type_help = (
    "Select which kind of analysis you want to see. This select box changes the content"
    " of the whole page (including time graph). If you select _total_, you will see sum"
    " of all metrics in the selected period, i.e. total spend of all Lebesgue shops in"
    " June 2023, and if you select _by shop_, the number displayed will"
    " correspond to the average metric by shop, i.e. how much an average shop spent in"
    " June 2023."
)


class ShopDescriptiveTab(DescriptiveTab):
    def show(self, shop_id: int):
        summary_df = self.get_summary_df(
            shop_id=shop_id,
            cache_id=type(self).__name__,
        )

        if not len(summary_df):
            return

        self.pie_charts(summary_df=summary_df.copy(), add_title=True)
        self.descriptive_features_through_time(summary_df=summary_df.copy())
        self.benchmarks(main_df=summary_df)

    @st.cache_data
    def get_summary_df(_self, shop_id: int, cache_id: str) -> pd.DataFrame:
        summary_df = _self.get_shop_descriptive_df(
            db=_self.db, shop_id=shop_id, start_date=_self.start_date, end_date=_self.end_date
        ).reset_index()
        if not len(summary_df):
            st.warning("No data.")
            return summary_df
        summary_df["year_month"] = summary_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))
        summary_df["feature_value"] = summary_df.feature_value.apply(get_frontend_name)
        for metric in metrics:
            summary_df[str(metric)] = summary_df.apply(metric.formula_series, axis=1)
        return summary_df

    @property
    def available_metrics(_self):
        return _self.metric_columns


class FacebookCreativeShopDescriptiveTab(ShopDescriptiveTab, FacebookCreativeDescriptive):
    ...


class FacebookTargetShopDescriptiveTab(ShopDescriptiveTab, FacebookTargetDescriptive):
    ...


class GoogleCampaignTypeShopDescriptiveTab(ShopDescriptiveTab, GoogleCampaignTypeDescriptive):
    ...


facebook_creative_shop_descriptive_tab = FacebookCreativeShopDescriptiveTab()
facebook_target_shop_descriptive_tab = FacebookTargetShopDescriptiveTab()
google_campaign_type_shop_descriptive_tab = GoogleCampaignTypeShopDescriptiveTab()
