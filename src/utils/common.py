import json
from numbers import Number
from typing import Any

import numpy as np


def print_dict(d: dict, indent: int = 4):
    print(json.dumps(d, indent=indent, cls=NpEncoder))


def recursively_apply_func(
    obj: Any,
    func: callable,
    apply_to_keys: bool = True,
    keys_for_whose_values_to_apply_func: list = [],
    keys_whose_values_to_leave_be: list = [],
    **kwargs,
) -> Any:
    """Applies function to all elements in object.

    Args:
        obj (Any): Object onto whose alements function will be applied.
        func (callable): Any callable. If applying function onto element raises Exception, this element
            will remain intact.
        apply_to_keys (bool, optional): Whether to apply this function onto keys of dictionaries in obj.
            Defaults to True.
        keys_for_whose_values_to_apply_func (list, optional): Any value under key in this list will be
        transformed by function func. If empty, all values under keys not in keys_whose_values_to_leave_be
        are transformed.
        keys_whose_values_to_leave_be (list, optional): Any value under key in this list will be
        returned as-is (without func modifying it). Defaults to [].

    Returns:
        Any: _description_
    Example:
        Args:
            obj = [1, {'k1': 'v1', 'k2': 'v2}],
            func=lambda x: x+'_applied',
            keys_for_which_to_ignore = ['k1']
            apply_to_keys: True
        Returns:
        [1, {'k1_applied': 'v1', 'k2_applied': 'v2_applied'}]
    """

    if type(obj) == list:
        return [
            recursively_apply_func(
                elem,
                func,
                apply_to_keys=apply_to_keys,
                keys_for_whose_values_to_apply_func=keys_for_whose_values_to_apply_func,
                keys_whose_values_to_leave_be=keys_whose_values_to_leave_be,
                **kwargs,
            )
            for elem in obj
        ]
    if type(obj) == tuple:
        return tuple(
            recursively_apply_func(
                elem,
                func,
                apply_to_keys=apply_to_keys,
                keys_for_whose_values_to_apply_func=keys_for_whose_values_to_apply_func,
                keys_whose_values_to_leave_be=keys_whose_values_to_leave_be,
                **kwargs,
            )
            for elem in obj
        )
    if type(obj) == dict:
        res = {}
        if not len(keys_for_whose_values_to_apply_func):
            local_keys_for_whose_values_to_apply_func = obj.keys() - set(keys_whose_values_to_leave_be)
        else:
            local_keys_for_whose_values_to_apply_func = keys_for_whose_values_to_apply_func

        for k in obj.keys():
            if apply_to_keys:
                try:
                    new_k = func(k)
                except Exception:
                    new_k = k
            else:
                new_k = k

            if k not in local_keys_for_whose_values_to_apply_func:
                res[new_k] = obj[k]
            else:
                res[new_k] = recursively_apply_func(
                    obj[k],
                    func,
                    apply_to_keys=apply_to_keys,
                    keys_for_whose_values_to_apply_func=keys_for_whose_values_to_apply_func,
                    keys_whose_values_to_leave_be=keys_whose_values_to_leave_be,
                    **kwargs,
                )
        return res
    try:
        res = func(obj, **kwargs)

        return res
    except Exception:
        return obj


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Returns JSON-serializable representation of the given object.
    Converts enums and dates to strings and NaNs to Nones.

    Returns:
        Any: of the same type as input object.
    """
    obj = recursively_apply_func(obj=obj, func=lambda x: np_encoder.default(x))
    obj = recursively_apply_func(obj=obj, func=lambda x: x.value if isinstance(x, Enum) else x)
    obj = recursively_apply_func(obj=obj, func=lambda x: x.strftime("%Y-%m-%d"))

    return obj


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Number) and np.isnan(obj):
            return None
        return json.JSONEncoder.default(self, obj)
