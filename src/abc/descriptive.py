from abc import ABC, abstractmethod, abstractproperty

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from src import crud
from src.database.session import db
from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.pingers import *
from src.utils import *


class DescriptiveDF(str, Enum):
    failed_shop_ids = "failed_shop_ids"
    main = "main"
    summary = "summary"


class FacebookImageDescriptiveDF(str, Enum):
    performance = "performance"
    filtered = "filtered"
    image = "image"
    filtered_image = "filtered_image"
    main = "main"
    summary = "summary"


class Descriptive(ABC):
    @abstractmethod
    def get_shop_df(db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        ...

    @abstractproperty
    def descriptive_columns(self) -> list[str]:
        ...

    @abstractproperty
    def tag(self) -> str:
        ...

    @abstractproperty
    def pie_columns(self) -> list[str]:
        ...

    s3_descriptive_folder = "descriptive"

    main_df_index = ["shop_id", "year_month", "feature", "feature_value"]

    metric_columns = [
        "spend_USD",
        "impr",
        "clicks",
        "purch",
        "purch_value_USD",
        "n_ads",
    ]

    n_months = 48
    performance_df_name = DescriptiveDF.main

    @property
    def end_date(self):
        # end_date should be the last day of the month so we always
        # only consider data from full months
        # TODO: remove timedelta
        today = date.today()
        end_date_plus_one = date(year=today.year, month=today.month, day=1)
        return end_date_plus_one - timedelta(days=1)

    @property
    def start_date(self):
        end_date_plus_one = self.end_date + timedelta(days=1)
        return end_date_plus_one - relativedelta(months=self.n_months)

    explode_descriptive_columns = []
    fake_feature = "fake_feature"
    db = db

    def get_shop_descriptive_df(
        self, db: Session, shop_id: int, start_date: date, end_date: date
    ) -> pd.DataFrame:
        shop_df = self.get_shop_df(db=db, shop_id=shop_id, start_date=start_date, end_date=end_date)
        if "shop_id" not in shop_df.columns:
            shop_df["shop_id"] = shop_id
        shop_df["n_ads"] = 1
        shop_descriptive_df = pd.DataFrame()

        if not len(shop_df):
            return shop_descriptive_df

        if len(
            (
                missing_columns := [
                    col
                    for col in self.descriptive_columns + self.metric_columns
                    if col not in shop_df.columns
                ]
            )
        ):
            logger.debug(f"{missing_columns = }")
            return shop_descriptive_df

        shop_df = shop_df[self.metric_columns + self.descriptive_columns + ["year_month", "shop_id"]]
        shop_df[self.fake_feature] = "."
        for explode_col in self.explode_descriptive_columns:
            shop_df[self.metric_columns] = shop_df[self.metric_columns].div(
                shop_df[explode_col].apply(len), axis=0
            )
            shop_df = shop_df.explode(explode_col).dropna(axis=0, subset=explode_col)
        stacked_df = (
            shop_df.set_index(
                list(set(shop_df.columns) - set(self.descriptive_columns + [self.fake_feature]))
            )
            .stack(level=-1)
            .reset_index()
        )
        level_column = [col for col in stacked_df.columns if "level" in str(col)][0]
        stacked_df.rename(columns={level_column: "feature", 0: "feature_value"}, inplace=True)
        shop_descriptive_df = stacked_df.groupby(self.main_df_index)[self.metric_columns].sum()

        return shop_descriptive_df

    def get_df_path(self, df_type: DescriptiveDF, end_date: date | None = None):
        if end_date is None:
            end_date = self.end_date
        return os.path.join(self.s3_descriptive_folder, self.tag, f"{end_date}_{df_type}.csv")

    def read_df(self, df_type: DescriptiveDF, end_date: date | None = None):
        return read_csv_from_s3(path=self.get_df_path(df_type=df_type, end_date=end_date))

    def get_available_dates(self, df_type: DescriptiveDF) -> list[date]:
        prefix = os.path.join(self.s3_descriptive_folder, self.tag)
        all_objects = list_objects_from_prefix(prefix=prefix)
        list_of_objects = [obj for obj in all_objects if df_type in obj]
        return [to_date(date_str) for date_str in extract_dates_from_str(" ".join(list_of_objects))]


class FacebookCreativeDescriptive(Descriptive):
    descriptive_columns = BOOLEAN_TEXT_FEATURES + ["creative_type", "target"]
    pie_columns = ["creative_type", "discount", "target"]
    tag = "facebook_creative"

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_facebook_creative_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            cast_to_date=False,
            enum_to_value=True,
        )


class FacebookTargetDescriptive(Descriptive):
    descriptive_columns = ["target", "gender", "audience", "age_groups"]
    explode_descriptive_columns = ["age_groups"]
    tag = "facebook_target"
    pie_columns = ["target", "audience", "gender"]

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_target_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            enum_to_value=True,
            cast_to_date=False,
        )


class GoogleCampaignTypeDescriptive(Descriptive):
    descriptive_columns = ["campaign_type"]
    tag = "google_campaign_type"
    pie_columns = ["campaign_type"]

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return crud.ga_daily_performance.get_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )


class FacebookImageDescriptive(Descriptive):
    descriptive_columns = ["color"]
    tag = "facebook_image"
    pie_columns = ["color"]
    n_ads_per_shop_and_month = 5

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_image_urls_and_ad_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )

    def get_shop_descriptive_df(self, **kwargs) -> pd.DataFrame:
        return self.get_shop_df(**kwargs)
