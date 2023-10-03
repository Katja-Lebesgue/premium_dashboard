import re
from datetime import date, datetime, timedelta


def to_date(x):
    if type(x) == str:
        x = datetime.strptime(x, "%Y-%m-%d").date()
    if type(x) == datetime:
        x = x.date()
    return x


def get_last_day_of_the_previous_month(dt: date) -> date:
    return date(year=dt.year, month=dt.month, day=1) - timedelta(days=1)


def extract_dates_from_str(text: str) -> list[str]:
    return [x.group() for x in re.finditer(r"(\d+(-)*)+", text)]
