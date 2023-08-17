from src.app.descriptive.descriptive_tab import DescriptiveTab
from src.abc.descriptive import FacebookCreativeDescriptive


class FacebookCreativeDescriptiveTab(DescriptiveTab, FacebookCreativeDescriptive):
    pie_columns = ["creative_type", "discount", "target"]


facebook_creative_descriptive_tab = FacebookCreativeDescriptiveTab()
