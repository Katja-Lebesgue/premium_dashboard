import pandas as pd
from datetime import datetime
from src.database.ad_creative_features_pingers.ping_my_creative_by_shop_id import (
    ping_my_creative_by_shop_id,
)
from src.utils.decorators import print_execution_time
from src.database.ad_creative_features_pingers.ping_my_creative_by_shop_id import (
    ping_my_creative_by_shop_id,
)
from src.database.pingers.ping_performance_data_by_shop_id import (
    ping_performance_data_by_shop_id,
)

from src.database.pingers.ping_target_by_shop_id import ping_target_by_shop_id

from src.database.myDB import DBConnect
from src.s3.read_by_shop import *


@print_execution_time
def ping_my_creative_and_performance_by_shop_id(
    shop_id: str | list[str],
) -> pd.DataFrame:

    creative = ping_my_creative_by_shop_id(shop_id)

    performance = ping_performance_data_by_shop_id(shop_id)
    performance["year_month"] = performance.year_month.apply(
        lambda x: datetime.strptime(x, "%Y-%m")
    )
    full = creative.merge(performance)

    full = add_creative_columns(full)
    full = add_performance_columns(full)

    return full
