from src.app.descriptive.descriptive_tab import DescriptiveTab
from src.abc.descriptive import FacebookTargetDescriptive


class FacebookTargetDescriptiveTab(DescriptiveTab, FacebookTargetDescriptive):
    pie_columns = ["target", "audience", "gender"]


facebook_target_descriptive_tab = FacebookTargetDescriptiveTab()
