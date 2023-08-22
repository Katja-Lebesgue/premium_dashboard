from src.app.benchmarks.benchmarks_tab import BenchmarksTab
from src.abc.descriptive import FacebookTargetDescriptive


class FacebookTargetBenchmarksTab(BenchmarksTab, FacebookTargetDescriptive):
    pass


facebook_target_benchmarks_tab = FacebookTargetBenchmarksTab()
