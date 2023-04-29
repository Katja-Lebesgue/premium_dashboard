import pandas as pd
from ast import literal_eval

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
