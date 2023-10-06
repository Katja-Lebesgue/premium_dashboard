from ast import literal_eval

import pandas as pd
from sqlalchemy.orm import Query, Session

dtypes = {"ad_id": str, "shop_id": str, "account_id": str, "target": str}


def read_csv_and_eval(path: str) -> pd.DataFrame:
    # reads csv using pd.read_csv and then uses ast.literal_eval() to evaluate all columns in df.

    df = pd.read_csv(path)
    str_cols = [col for col, type in dtypes.items() if type == str]
    cols_to_eval = list(set(df.columns) - set(str_cols))
    df.loc[:, cols_to_eval] = df.loc[:, cols_to_eval].applymap(eval_but_leave_string_if_you_cant)
    return df


def eval_but_leave_string_if_you_cant(text: str):
    try:
        out = literal_eval(text)
    except:
        out = text

    return out


def read_query_into_df(db: Session, query: Query, chunk_size: int = 5000) -> pd.DataFrame:
    n_rows = query.count()
    df = pd.DataFrame()
    for offset in range(0, n_rows + 1, chunk_size):
        new_df = pd.read_sql(query.offset(offset).limit(chunk_size).statement, db.bind)
        df = pd.concat([df, new_df], axis=0)
    return df
