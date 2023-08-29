def ping_facebook_creative_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    cast_to_date: bool = True,
    enum_to_value: bool = False,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_facebook_creative_and_performance!")
        return None

    creative = ping_facebook_creative(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        enum_to_value=enum_to_value,
    )

    if len(creative) == 0:
        return creative

    performance = crud.fb_daily_performance.get_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
        cast_to_date=cast_to_date,
    )

    if len(performance) == 0:
        return creative

    df = creative.merge(performance)

    return df
