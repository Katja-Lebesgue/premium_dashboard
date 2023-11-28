from abc import ABC, abstractmethod, abstractproperty

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from src import crud
from src.database.session import db
from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.pingers import *
from src.utils import *
from src.interfaces.s3_reader_writer import S3ReaderWriter


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


class Descriptive(ABC, S3ReaderWriter):
    @abstractproperty
    def descriptive_columns(self) -> list[str]:
        ...

    @abstractproperty
    def pie_columns(self) -> list[str]:
        ...

    @abstractproperty
    def tag(self) -> str:
        ...

    @property
    def s3_folder(self) -> str:
        return os.path.join(self.s3_descriptive_folder, self.tag)

    def get_raw_shop_df(self, db: Session, shop_id: int) -> pd.DataFrame:
        ...

    s3_descriptive_folder = "descriptive"

    main_df_index = ["shop_id", "year_month", "feature", "feature_value"]

    metrics = (cr, ctr, cpm, cac, roas)

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

    def get_shop_df(self, db: Session, shop_id: int, **kwargs) -> pd.DataFrame:
        start_date = self.start_date
        end_date = self.end_date
        raw_shop_df = self.get_raw_shop_df(db=db, shop_id=shop_id)
        if "shop_id" not in raw_shop_df.columns:
            raw_shop_df["shop_id"] = shop_id
        raw_shop_df["n_ads"] = 1
        shop_df = pd.DataFrame()

        if not len(raw_shop_df):
            return shop_df

        if len(
            (
                missing_columns := [
                    col
                    for col in self.descriptive_columns + self.metric_columns
                    if col not in raw_shop_df.columns
                ]
            )
        ):
            logger.debug(f"{missing_columns = }")
            return shop_df

        raw_shop_df = raw_shop_df[self.metric_columns + self.descriptive_columns + ["year_month", "shop_id"]]
        raw_shop_df[self.fake_feature] = "."
        for explode_col in self.explode_descriptive_columns:
            raw_shop_df[self.metric_columns] = raw_shop_df[self.metric_columns].div(
                raw_shop_df[explode_col].apply(len), axis=0
            )
            raw_shop_df = raw_shop_df.explode(explode_col).dropna(axis=0, subset=explode_col)
        stacked_df = (
            raw_shop_df.set_index(
                list(set(raw_shop_df.columns) - set(self.descriptive_columns + [self.fake_feature]))
            )
            .stack(level=-1)
            .reset_index()
        )
        level_column = [col for col in stacked_df.columns if "level" in str(col)][0]
        stacked_df.rename(columns={level_column: "feature", 0: "feature_value"}, inplace=True)
        shop_df = (
            stacked_df.groupby(self.main_df_index, dropna=False)[self.metric_columns].sum().reset_index()
        )

        return shop_df

    def create_and_save_summary(self) -> pd.DataFrame:
        main_df = self.read_df(df_type=DescriptiveDF.main, df_id=self.end_date)
        main_df["n_shops"] = 1

        absolute_sum_by_shop_and_value = main_df.set_index(
            ["shop_id", "year_month", "feature", "feature_value"]
        )[self.metric_columns + ["n_shops"]]

        # absolute monthly sums
        absolute_sum_by_value = main_df.groupby(["year_month", "feature", "feature_value"]).sum()[
            self.metric_columns + ["n_shops"]
        ]

        # get df of relative values by shop
        sum_by_shop_and_feature = main_df.groupby(["shop_id", "year_month", "feature"])[
            self.metric_columns
        ].sum()

        relative_sum_by_shop_and_value = (
            absolute_sum_by_shop_and_value[self.metric_columns] / sum_by_shop_and_feature
        )

        # get df of relative sums without shop
        relative_sum_by_value = (
            relative_sum_by_shop_and_value.reset_index()
            .groupby(["year_month", "feature", "feature_value"])[self.metric_columns]
            .sum()
        )

        # normalize them by dividing by numnber of shops per month per feature
        n_shops_by_month_and_feature = (
            relative_sum_by_value.reset_index().groupby(["year_month", "feature"])[self.metric_columns].sum()
        )
        normalised_relative_sum_by_value = relative_sum_by_value.div(n_shops_by_month_and_feature, axis=0)
        normalised_relative_sum_by_value.rename(
            columns={col: col + "_by_shop" for col in self.metric_columns}, inplace=True
        )

        # join the two to get the final result
        summary_df = absolute_sum_by_value.join(normalised_relative_sum_by_value)
        self.save_df(df=summary_df, df_type=DescriptiveDF.summary, df_id=self.end_date, index=True)
        return summary_df

    # main function
    def save_for_all_shops(
        self,
        db: Session,
        force_from_scratch: bool = False,
        repeat_for_failed: bool = False,
        df_type: str = DescriptiveDF.main,
        save_to_s3: bool = True,
        testing: bool = False,
    ) -> pd.DataFrame:
        return super().save_for_all_shops(
            df_id=self.end_date,
            db=db,
            force_from_scratch=force_from_scratch,
            repeat_for_failed=repeat_for_failed,
            df_type=df_type,
            save_to_s3=save_to_s3,
            testing=testing,
        )


class FacebookCreativeDescriptive(Descriptive):
    descriptive_columns = BOOLEAN_TEXT_FEATURES + ["creative_type", "target", "discount_list"]
    pie_columns = ["creative_type", "discount", "target"]
    explode_descriptive_columns = ["discount_list"]
    tag = "facebook_creative"

    def get_raw_shop_df(self, db: Session, shop_id: int) -> pd.DataFrame:
        return ping_facebook_creative_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=self.start_date,
            end_date=self.end_date,
            cast_to_date=False,
            enum_to_value=True,
        )


class FacebookTargetDescriptive(Descriptive):
    descriptive_columns = ["target", "gender", "audience", "age_groups"]
    explode_descriptive_columns = ["age_groups"]
    tag = "facebook_target"
    pie_columns = ["target", "audience", "gender"]

    def get_raw_shop_df(self, db: Session, shop_id: int) -> pd.DataFrame:
        return ping_target_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=self.start_date,
            end_date=self.end_date,
            enum_to_value=True,
            cast_to_date=False,
        )


class GoogleCampaignTypeDescriptive(Descriptive):
    descriptive_columns = ["campaign_type"]
    tag = "google_campaign_type"
    pie_columns = ["campaign_type"]
    skip_shop_ids = [42787782]

    def get_raw_shop_df(self, db: Session, shop_id: int) -> pd.DataFrame:
        return crud.ga_daily_performance.get_performance(
            db=db, shop_id=shop_id, start_date=self.start_date, end_date=self.end_date
        )


class FacebookImageDescriptive(Descriptive):
    descriptive_columns = ["color"]
    tag = "facebook_image"
    pie_columns = ["color"]
    n_ads_per_shop_and_month = 5

    def get_shop_df(self, db: Session, shop_id: int, **kwargs) -> pd.DataFrame:
        return ping_image_urls_and_ad_performance(
            db=db, shop_id=shop_id, start_date=self.start_date, end_date=self.end_date
        )


facebook_creative_descriptive = FacebookCreativeDescriptive()
facebook_target_descriptive = FacebookTargetDescriptive()
google_campaign_type_descriptive = GoogleCampaignTypeDescriptive()
facebook_image_descriptive = FacebookImageDescriptive()
