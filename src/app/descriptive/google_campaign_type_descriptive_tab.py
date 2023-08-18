from src.app.descriptive.descriptive_tab import DescriptiveTab
from src.abc.descriptive import GoogleCampaignTypeDescriptive


class GoogleCampaignTypeDescriptiveTab(DescriptiveTab, GoogleCampaignTypeDescriptive):
    pie_columns = ["campaign_type"]


google_campaign_type_descriptive_tab = GoogleCampaignTypeDescriptiveTab()
