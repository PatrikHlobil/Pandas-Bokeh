import re

from pandas import DataFrame


def _extract_additional_columns(df: DataFrame, hovertool_string: str):
    additional_columns = []
    if hovertool_string is not None:
        if not isinstance(hovertool_string, str):
            raise ValueError("<hovertool_string> can only be None or a string.")
        # Search for hovertool_string columns in DataFrame:
        for s in re.findall(r"@[^\s\{]+", hovertool_string):
            s = s[1:]
            if s in df.columns:
                additional_columns.append(s)
        for s in re.findall(r"@\{.+\}", hovertool_string):
            s = s[2:-1]
            if s in df.columns:
                additional_columns.append(s)
    return additional_columns
