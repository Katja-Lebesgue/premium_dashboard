def row_to_dict(row) -> dict:
    d = row.__dict__
    print(d.keys())
    d.pop("_sa_instance_state")
    return d
