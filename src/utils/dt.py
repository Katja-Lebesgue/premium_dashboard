from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def to_date(x):
    if type(x) == str:
        x = datetime.strptime(x, "%Y-%m-%d").date()
    if type(x) == datetime:
        x = x.date()
    return x
