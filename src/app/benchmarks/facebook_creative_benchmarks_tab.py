from src.app.benchmarks.benchmarks_tab import BenchmarksTab
from src.abc.descriptive import FacebookCreativeDescriptive


class FacebookCreativeBenchmarksTab(BenchmarksTab, FacebookCreativeDescriptive):
    pass


facebook_creative_benchmarks_tab = FacebookCreativeBenchmarksTab()
