from datetime import date
from enum import Enum

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.feature_extractors import *
from src.models import *
from src.models.enums.facebook import Target
from src.utils import MyInterval, convert_enum_to_its_value, element_to_list, recursively_apply_func
from src.utils import *


class Audience(str, Enum):
    broad = "broad"
    lookalike = "lookalike"
    interest = "interest"
    retargeting = "retargeting"


class AgeGroup(str, Enum):
    young = "young"
    middle = "middle"
    old = "old"


agegroup_interval_dict = {
    AgeGroup.young: MyInterval(13, 30),
    AgeGroup.middle: MyInterval(30, 48),
    AgeGroup.old: MyInterval(48, 65),
}


class Gender(str, Enum):
    male = "male"
    female = "female"
    both = "both"


def ping_target(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    enum_to_value: bool = False,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_target!")
        return None

    query = db.query(
        FacebookAdset.shop_id,
        FacebookAdset.account_id,
        FacebookAdset.adset_id,
        FacebookAdset.target,
        FacebookAdset.targeting,
    )

    if start_date is not None:
        query = query.join(
            FacebookDailyPerformance,
            (FacebookAdset.adset_id == FacebookDailyPerformance.adset_id)
            & (FacebookAdset.account_id == FacebookDailyPerformance.account_id),
        ).filter(FacebookDailyPerformance.date_start.between(start_date, end_date))

    filters = []

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        adset_ids_query = db.query(FacebookAd.adset_id).filter(FacebookAd.ad_id.in_(ad_id))
        adset_ids_df = read_query_into_df(db=db, query=adset_ids_query)
        adset_ids = adset_ids_df.adset_id.tolist()
        filters.append(FacebookAdset.adset_id.in_(adset_ids))
    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        filters.append(FacebookAdset.shop_id.in_(shop_id))
    if len(filters):
        query = query.filter(*filters)

    df = read_query_into_df(db=db, query=query.distinct(FacebookAdset.adset_id))

    if len(df) == 0:
        return df

    audience_and_interests = df.apply(
        lambda df: deduce_audience(target=df.target, targeting=df.targeting), axis=1
    )
    df = df.join(audience_and_interests.apply(pd.Series))

    df["gender"] = df.targeting.apply(lambda x: deduce_gender(x))
    df["age_groups"] = df.targeting.apply(lambda x: get_agegroups(x))
    df["countries"] = df.targeting.apply(lambda d: d.get("geo_locations", {}).get("countries", []))

    if enum_to_value:
        df = df.applymap(lambda x: recursively_apply_func(obj=x, func=convert_enum_to_its_value))

    return df


def deduce_gender(targeting: list | None = None):
    gender_list = targeting.get("genders")
    if type(gender_list) != list or len(gender_list) != 1:
        return Gender.both
    if gender_list[0] == 2:
        return Gender.female
    if gender_list[0] == 1:
        return Gender.male
    return Gender.both


def deduce_audience(targeting: dict, target: Target) -> Audience:
    if target == Target.remarketing:
        return {"audience": Audience.retargeting, "interests": []}
    flexible_spec = targeting.get("flexible_spec", [])
    interest_dicts = [d.get("interests", []) for d in flexible_spec if type(d) == dict]
    interests_packed = [[d.get("name") for d in interest] for interest in interest_dicts]
    interests = [interest for interest in sum(interests_packed, []) if interest is not None]
    if len(interests):
        return {"interests": interests, "audience": Audience.interest}

    custom_audiences = targeting.get("custom_audiences", [])
    custom_audiences_names = [d.get("name", "") for d in custom_audiences if type(d) == dict]
    if any(["lookalike" in ca_name.lower() for ca_name in custom_audiences_names]):
        return {"audience": Audience.lookalike, "interests": []}
    return {"audience": Audience.broad, "interests": []}


def get_agegroups(targeting: dict) -> list[AgeGroup]:
    age_min = targeting.get("age_min")
    age_max = targeting.get("age_max")
    if age_min is None or age_max is None:
        return []
    age_interval = MyInterval(age_min, age_max)
    age_groups = []
    for agegroup, agegroup_interval in agegroup_interval_dict.items():
        if (
            age_interval.mid in agegroup_interval
            or (age_interval & agegroup_interval).length / agegroup_interval.length > 0.3
        ):
            age_groups.append(agegroup)
    return age_groups
