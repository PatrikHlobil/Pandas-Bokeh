import datetime
import numbers
import re
from typing import Iterable, List, Optional, Union

import numpy as np
import pandas as pd
from bokeh.models import Range1d, RangeTool
from bokeh.palettes import all_palettes
from bokeh.plotting import figure
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


def _determine_data_columns(
    y: Optional[Union[str, Iterable[str]]], df: pd.DataFrame
) -> List[str]:
    if y is None:
        cols = df.columns
    elif not isinstance(y, (list, tuple)):
        cols = [y]
    else:
        cols = y
    data_cols = []
    for col in cols:
        if col not in df.columns:
            raise ValueError(
                f"Could not find '{col}' in the columns of the provided DataFrame/Series. Please provide for the <y> parameter either a column name of the DataFrame/Series or an array of the same length."
            )
        if hasattr(df[col].dtype, "_is_numeric") and df[col].dtype._is_numeric:
            data_cols.append(col)
        elif hasattr(df[col].dtype, "_is_numeric") and not df[col].dtype._is_numeric:
            continue
        elif np.issubdtype(df[col].dtype, np.number):
            data_cols.append(col)
    if len(data_cols) == 0:
        raise ValueError("No numeric data columns found for plotting.")
    return data_cols


def check_type(data):
    """Checks type of provided data array."""

    first_value = np.array(data)[0]

    if isinstance(first_value, numbers.Number):
        return "numeric"
    elif isinstance(first_value, (np.datetime64, datetime.datetime, datetime.date)):
        return "datetime"
    else:
        return "object"


def get_colormap(colormap, N_cols):

    """Returns a colormap with <N_cols> colors. <colormap> can be either None,
    a string with the name of a Bokeh color palette or a list/tuple of colors."""

    if colormap is None:
        if N_cols <= 10:
            colormap = all_palettes["Category10"][10][:N_cols]
        elif N_cols <= 20:
            colormap = all_palettes["Category20"][N_cols]
        else:
            colormap = all_palettes["Category20"][20] * int(N_cols / 20 + 1)
            colormap = colormap[:N_cols]
    elif isinstance(colormap, str):
        if colormap in all_palettes:
            colormap = all_palettes[colormap]
            max_key = max(colormap.keys())
            if N_cols <= max_key:
                colormap = colormap[N_cols]
            else:
                colormap = colormap[max_key]
                colormap = colormap * int(N_cols / len(colormap) + 1)
                colormap = colormap[:N_cols]
        else:
            raise ValueError(
                f"Could not find <colormap> with name {colormap}. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): {list(all_palettes.keys())}"
            )
    elif isinstance(colormap, (list, tuple)):
        colormap = colormap * int(N_cols / len(colormap) + 1)
        colormap = colormap[:N_cols]
    else:
        raise ValueError(
            "<colormap> can onyl be None, a name of a colorpalette as string( see https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ) or a list/tuple of colors."
        )

    return colormap


def _times_to_string(times):

    types = []
    for t in times:
        t = pd.to_datetime(t)
        if t.microsecond > 0:
            types.append("microsecond")
        elif t.second > 0:
            types.append("second")
        elif t.hour > 0:
            types.append("hour")
        else:
            types.append("date")

    if "microsecond" in types:
        return [pd.to_datetime(t).strftime("%Y/%m/%d %H:%M:%S.%f") for t in times]
    elif "second" in types:
        return [pd.to_datetime(t).strftime("%Y/%m/%d %H:%M:%S") for t in times]
    elif "hour" in types:
        return [pd.to_datetime(t).strftime("%Y/%m/%d %H:%M") for t in times]
    elif "date" in types:
        return [pd.to_datetime(t).strftime("%Y/%m/%d") for t in times]


def _initialize_rangetool(p, x_axis_type, source):
    """
    Initializes the range tool chart and slider.

    Parameters
    ----------
    p : Bokeh.plotting.figure
        Bokeh plot that the figure tool is going to supplement.
    x_axis_type : str
        Type of the xaxis (ex. datetime)
    source : Bokeh.models.sources
        Data

    Returns
    -------
        Bokeh.plotting.figure
    """
    # Initialize range tool plot
    p_rangetool = figure(
        title="Drag the box to change the range above.",
        plot_height=130,
        plot_width=p.plot_width,
        y_range=p.y_range,
        x_axis_type=x_axis_type,
        y_axis_type=None,
        tools="",
        toolbar_location=None,
    )

    # Need to explicitly set the initial range of the plot for the range tool.
    start_index = int(0.75 * len(source["__x__values"]))
    p.x_range = Range1d(source["__x__values"][start_index], source["__x__values"][-1])

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    p_rangetool.ygrid.grid_line_color = None
    p_rangetool.add_tools(range_tool)
    p_rangetool.toolbar.active_multi = range_tool

    return p_rangetool
