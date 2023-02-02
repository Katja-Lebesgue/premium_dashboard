def hide_table_row_index():

    css_string = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

    return css_string


def style_small_values(value: float, props: str = "") -> str:
    return props if value is not None and value < 0.1 else None
