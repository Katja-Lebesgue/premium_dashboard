from src.app.benchmarks.benchmarks_tab import BenchmarksTab
from src.abc.descriptive import GoogleCampaignTypeDescriptive


class GoogleCampaignTypeBenchmarksTab(BenchmarksTab, GoogleCampaignTypeDescriptive):
    pass


google_campaign_type_benchmarks_tab = GoogleCampaignTypeBenchmarksTab()
