#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import numbers
import re
import warnings
from copy import deepcopy
from typing import Iterable, List, Optional, Union

import numpy as np
import pandas as pd
from bokeh.core.properties import value as _value
from bokeh.layouts import column
from bokeh.models import (
    ColorBar,
    ColumnDataSource,
    DatetimeTickFormatter,
    FuncTickFormatter,
    HoverTool,
    LinearColorMapper,
    RangeTool,
)
from bokeh.models.ranges import Range1d
from bokeh.palettes import Inferno256, all_palettes
from bokeh.plotting import figure
from bokeh.transform import cumsum, dodge
from pandas.core.base import PandasObject
from pandas.errors import ParserError

from .base import embedded_html, set_fontsizes_of_figure, show
from .geoplot import geoplot


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


def plot(  # noqa C901
    df_in,
    x=None,
    y=None,
    kind="line",
    figsize=None,
    use_index=True,
    title="",
    legend="top_right",
    logx=False,
    logy=False,
    xlabel=None,
    ylabel=None,
    xticks=None,
    yticks=None,
    xlim=None,
    ylim=None,
    fontsize_title=None,
    fontsize_label=None,
    fontsize_ticks=None,
    fontsize_legend=None,
    color=None,
    colormap=None,
    category=None,
    histogram_type=None,
    stacked=False,
    weights=None,
    bins=None,
    normed=False,
    cumulative=False,
    show_average=False,
    plot_data_points=False,
    plot_data_points_size=5,
    number_format=None,
    disable_scientific_axes=None,
    show_figure=True,
    return_html=False,
    panning=True,
    zooming=True,
    sizing_mode="fixed",
    toolbar_location="right",
    hovertool=True,
    hovertool_string=None,
    rangetool=False,
    vertical_xlabel=False,
    x_axis_location="below",
    webgl=True,
    reuse_plot=None,  # This keyword is not used by Pandas-Bokeh, but pandas plotting API adds it for series object calls
    **kwargs,
):
    """Method for creating a interactive with 'Bokeh' as plotting backend. Available
    plot kinds are:

    * line
    * point
    * scatter
    * bar / barh
    * hist
    * area
    * pie
    * map

    Examples
    --------
    >>> df.plot_bokeh.line()
    >>> df.plot_bokeh.scatter(x='x',y='y')

    These plotting methods can also be accessed by calling the accessor as a
    method with the ``kind`` argument (except of "map" plot):
    ``df.plot_bokeh(kind='line')`` is equivalent to ``df.plot_bokeh.line()``

    For more information about the individual plot kind implementations, have a
    look at the underlying method accessors (like df.plot_bokeh.line) or visit
    https://github.com/PatrikHlobil/Pandas-Bokeh.

    If `sizing_mode` is not fixed (default), it will overide the set plot width or height
    depending on which axis it is scaled on.

    """

    # Make a local copy of the DataFrame:
    df = df_in.copy()
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    if kind == "map":
        return mapplot(
            df,
            x=x,
            y=y,
            figsize=figsize,
            title=title,
            legend=legend,
            xlabel=xlabel,
            ylabel=ylabel,
            xlim=xlim,
            color=color,
            colormap=colormap,
            category=category,
            show_figure=show_figure,
            return_html=return_html,
            panning=panning,
            zooming=zooming,
            toolbar_location=toolbar_location,
            hovertool=hovertool,
            hovertool_string=hovertool_string,
            webgl=webgl,
            **kwargs,
        )

    # Check plot kind input:
    allowed_kinds = [
        "line",
        "step",
        "point",
        "scatter",
        "bar",
        "barh",
        "hist",
        "area",
        "pie",
        "map",
    ]

    rangetool_allowed_kinds = ["line", "step"]

    if kind not in allowed_kinds:
        allowed_kinds = "', '".join(allowed_kinds)
        raise ValueError(f"Allowed plot kinds are '{allowed_kinds}'.")

    if rangetool and kind not in rangetool_allowed_kinds:
        allowed_rangetool_kinds = "', '".join(rangetool_allowed_kinds)
        raise ValueError(
            f"For using the rangetool, the allowed plot kinds are '{allowed_rangetool_kinds}'."
        )

    if rangetool:
        x_axis_location = "above"

    # Get and check options for base figure:
    figure_options = {
        "title": title,
        "toolbar_location": toolbar_location,
        "active_scroll": "wheel_zoom",
        "plot_width": 600,
        "plot_height": 400,
        "output_backend": "webgl",
        "sizing_mode": sizing_mode,
        "x_axis_location": x_axis_location,
    }
    # Initializing rangetool plot variable:
    p_rangetool = None

    if figsize is not None:
        width, height = figsize
        figure_options["plot_width"] = width
        figure_options["plot_height"] = height
    if logx:
        figure_options["x_axis_type"] = "log"
    if logy:
        figure_options["y_axis_type"] = "log"
    if xlabel is not None:
        figure_options["x_axis_label"] = xlabel
    if ylabel is not None:
        figure_options["y_axis_label"] = ylabel
    if xlim is not None:
        if not isinstance(xlim, (tuple, list)):
            raise ValueError("<xlim> must be a list/tuple of form (x_min, x_max).")
        elif len(xlim) != 2:
            raise ValueError("<xlim> must be a list/tuple of form (x_min, x_max).")
        else:
            figure_options["x_range"] = xlim
    if ylim is not None:
        if not isinstance(ylim, (tuple, list)):
            raise ValueError("<ylim> must be a list/tuple of form (y_min, y_max).")
        elif len(ylim) != 2:
            raise ValueError("<ylim> must be a list/tuple of form (y_min, y_max).")
        else:
            figure_options["y_range"] = ylim
    if webgl:
        figure_options["output_backend"] = "webgl"
    if number_format is None:
        number_format = ""
    else:
        number_format = "{%s}" % number_format

    # Check hovertool_string and define additional columns to keep in source:
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

    # Set standard linewidth:
    if "line_width" not in kwargs:
        kwargs["line_width"] = 2

    # Get x-axis Name and Values:
    delete_in_y = None
    if x is not None:
        if issubclass(x.__class__, pd.Index) or issubclass(x.__class__, pd.Series):
            if x.name is not None:
                name = str(x.name)
            else:
                name = ""
            x = x.values
        elif x in df.columns:
            delete_in_y = x
            name = str(x)
            x = df[x].values
        elif isinstance(x, (tuple, list, type(np.array))):
            if len(x) == len(df):
                x = x
                name = ""
            else:
                raise Exception(
                    "Length of provided <x> argument does not fit length of DataFrame or Series."
                )
        else:
            raise Exception(
                "Please provide for the <x> parameter either a column name of the DataFrame/Series or an array of the same length."
            )
    else:
        if use_index:
            x = df.index.values
            if df.index.name is not None:
                name = str(df.index.name)
            else:
                name = ""
        else:
            x = np.linspace(0, len(df) - 1, len(df))
            name = ""

    # Define name of axis of x-values (for horizontal plots like barh, this corresponds
    # to y-axis):
    if kind == "barh":
        if "y_axis_label" not in figure_options:
            figure_options["y_axis_label"] = name

    else:
        if "x_axis_label" not in figure_options:
            figure_options["x_axis_label"] = name

    # Check type of x-axis:
    if check_type(x) == "datetime":
        figure_options["x_axis_type"] = "datetime"
        xaxis_type = "datetime"
        if xlim is not None:
            starttime, endtime = xlim
            try:
                starttime = pd.to_datetime(starttime)
            except ParserError:
                raise ValueError("Could not parse x_min input of <xlim> as datetime.")
            try:
                endtime = pd.to_datetime(endtime)
            except ParserError:
                raise ValueError("Could not parse x_max input of <xlim> as datetime.")
            figure_options["x_range"] = (starttime, endtime)

    elif check_type(x) == "numeric":
        xaxis_type = "numerical"
    else:
        xaxis_type = "categorical"

    if kind in ["bar", "barh", "pie"]:
        xaxis_type = "categorical"

    x_old = x
    x_labels_dict = None
    if xaxis_type == "categorical":
        if check_type(x) == "datetime":
            x = _times_to_string(x)
        else:
            x = [str(el) for el in x]
        if kind != "hist":
            x_labels_dict = dict(zip(range(len(x)), x))
            x = list(range(len(x)))
        if "x_axis_type" in figure_options:
            del figure_options["x_axis_type"]

    # Determine data cols to plot (only plot numeric data):
    data_cols = _determine_data_columns(y, df)

    # Convert y-column names into string representation:
    df.rename(columns={col: str(col) for col in data_cols}, inplace=True)
    data_cols = [str(col) for col in data_cols]

    # Delete x column if it appears in y columns:
    if delete_in_y is not None:
        if delete_in_y in data_cols:
            data_cols.remove(delete_in_y)
    N_cols = len(data_cols)
    if len(data_cols) == 0:
        raise Exception(
            f"The only numeric column is the column {delete_in_y} that is already used on the x-axis."
        )

    # Autodetect y-label if no y-label is provided by user and only one y-column exists:
    if N_cols == 1:
        if kind == "barh":
            if "x_axis_label" not in figure_options:
                figure_options["x_axis_label"] = data_cols[0]
        else:
            if "y_axis_label" not in figure_options:
                figure_options["y_axis_label"] = data_cols[0]

    # Get Name of x-axis data:
    if kind == "barh":
        xlabelname = (
            figure_options["y_axis_label"]
            if figure_options.get("y_axis_label", "") != ""
            else "x"
        )
    else:
        xlabelname = (
            figure_options["x_axis_label"]
            if figure_options.get("x_axis_label", "") != ""
            else "x"
        )

    # Create Figure for plotting:
    p = figure(**figure_options)
    if "x_axis_type" not in figure_options:
        figure_options["x_axis_type"] = None

    # For categorical plots, set the xticks:
    if x_labels_dict is not None:
        p.xaxis.formatter = FuncTickFormatter(
            code="""
                                var labels = %s;
                                return labels[tick];
                                """
            % x_labels_dict
        )

    # Define ColumnDataSource for Plot if kind != "hist":
    if kind != "hist":
        source = {col: df[col].values for col in data_cols}
        source["__x__values"] = x
        source["__x__values_original"] = x_old
        for kwarg, value in kwargs.items():
            if value in df.columns:
                source[value] = df[value].values
        for add_col in additional_columns:
            source[add_col] = df[add_col].values

    # Define colormap
    if kind not in ["scatter", "pie"]:
        colormap = get_colormap(colormap, N_cols)

    if color is not None:
        colormap = get_colormap([color], N_cols)

    # Add Glyphs to Plot:
    if kind == "line":
        p, p_rangetool = lineplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            xlabelname,
            figure_options["x_axis_type"],
            plot_data_points,
            plot_data_points_size,
            hovertool_string,
            number_format,
            rangetool,
            **kwargs,
        )

    if kind == "step":
        p, p_rangetool = stepplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            xlabelname,
            figure_options["x_axis_type"],
            plot_data_points,
            plot_data_points_size,
            hovertool_string,
            number_format,
            rangetool,
            **kwargs,
        )

    if kind == "point":
        p = pointplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            hovertool_string,
            xlabelname,
            figure_options["x_axis_type"],
            number_format,
            **kwargs,
        )

    if kind == "scatter":

        if N_cols > 2:
            raise Exception(
                "For scatterplots <x> and <y> values can only be a single column of the DataFrame, not a list of columns. Please specify both <x> and <y> columns for a scatterplot uniquely."
            )

        # Get and set y-labelname:
        y_column = data_cols[0]
        if "y_axis_label" not in figure_options:
            p.yaxis.axis_label = y_column

        # Get values for y-axis:
        y = df[y_column].values

        # Delete additionally created values by pandas.plotting:
        for add_param in ["s", "c"]:
            if add_param in kwargs:
                del kwargs[add_param]

        # Get values for categorical colormap:
        category_values = None
        if category in df.columns:
            category_values = df[category].values
        elif category is not None:
            raise Exception(
                "<category> parameter has to be either None or the name of a single column of the DataFrame"
            )

        scatterplot(
            p,
            df,
            x,
            x_old,
            y,
            category,
            category_values,
            colormap,
            hovertool,
            hovertool_string,
            additional_columns,
            x_axis_type=figure_options["x_axis_type"],
            xlabelname=xlabelname,
            ylabelname=y_column,
            **kwargs,
        )

    if kind == "bar" or kind == "barh":

        # Define data source for barplot:
        data = {col: df[col].values for col in data_cols}
        data["__x__values"] = x
        data["__x__values_original"] = x_old
        source = ColumnDataSource(data)
        for kwarg, value in kwargs.items():
            if value in df.columns:
                source.data[value] = df[value].values
        for add_col in additional_columns:
            source.data[add_col] = df[add_col].values

        # Create Figure (just for categorical barplots):
        del figure_options["x_axis_type"]
        if "y_axis_label" not in figure_options and kind == "barh":
            figure_options["y_axis_label"] = xlabelname
        p = figure(**figure_options)
        figure_options["x_axis_type"] = None

        # Set xticks:
        if kind == "bar":
            p.xaxis.formatter = FuncTickFormatter(
                code="""
                                    var labels = %s;
                                    return labels[tick];
                                    """
                % x_labels_dict
            )
        elif kind == "barh":
            p.yaxis.formatter = FuncTickFormatter(
                code="""
                                    var labels = %s;
                                    return labels[tick];
                                    """
                % x_labels_dict
            )

        if not stacked:
            if N_cols >= 3:
                base_width = 0.5
            else:
                base_width = 0.35
            width = base_width / (N_cols - 0.5)
            if N_cols == 1:
                shifts = [0]
            else:
                delta_shift = base_width / (N_cols - 1)
                shifts = [-base_width / 2 + i * delta_shift for i in range(N_cols)]

            for i, name, color, shift in zip(
                range(N_cols), data_cols, colormap, shifts
            ):
                if kind == "bar":
                    glyph = p.vbar(
                        x=dodge("__x__values", shift, range=p.x_range),
                        top=name,
                        width=width,
                        source=source,
                        color=color,
                        legend_label=" " + name,
                        **kwargs,
                    )
                    hovermode = "vline"

                elif kind == "barh":
                    glyph = p.hbar(
                        y=dodge("__x__values", shift, range=p.y_range),
                        right=name,
                        height=width,
                        source=source,
                        color=color,
                        legend_label=" " + name,
                        **kwargs,
                    )
                    hovermode = "hline"

                if hovertool:
                    my_hover = HoverTool(mode=hovermode, renderers=[glyph])
                    if hovertool_string is None:
                        my_hover.tooltips = [
                            (xlabelname, "@__x__values_original"),
                            (name, "@{%s}" % name),
                        ]
                    else:
                        my_hover.tooltips = hovertool_string
                    p.add_tools(my_hover)

        if stacked:

            if kind == "bar":
                glyph = p.vbar_stack(
                    data_cols,
                    x="__x__values",
                    width=0.8,
                    source=source,
                    color=colormap,
                    legend_label=data_cols,
                    **kwargs,
                )
                hovermode = "vline"

            elif kind == "barh":
                glyph = p.hbar_stack(
                    data_cols,
                    y="__x__values",
                    height=0.8,
                    source=source,
                    color=colormap,
                    legend_label=data_cols,
                    **kwargs,
                )
                hovermode = "hline"

            if hovertool:
                my_hover = HoverTool(mode=hovermode, renderers=[glyph[-1]])
                if hovertool_string is None:
                    my_hover.tooltips = [(xlabelname, "@__x__values_original")] + [
                        (col, "@{%s}" % col) for col in data_cols
                    ]
                else:
                    my_hover.tooltips = hovertool_string
                p.add_tools(my_hover)

    if kind == "hist":

        # Disable line_color (for borders of histogram bins) per default:
        if "line_color" not in kwargs:
            kwargs["line_color"] = None
        elif kwargs["line_color"] is True:
            del kwargs["line_color"]

        if "by" in kwargs and y is None:
            y = kwargs["by"]
            del kwargs["by"]

        # Check for stacked keyword:
        if stacked and histogram_type not in [None, "stacked"]:
            warnings.warn(
                f"<histogram_type> was set to '{histogram_type}', but was overriden by <stacked>=True parameter."
            )
            histogram_type = "stacked"
        elif stacked and histogram_type is None:
            histogram_type = "stacked"

        # Set xlabel if only one y-column is given and user does not override this via
        # xlabel parameter:
        if len(data_cols) == 1 and xlabel is None:
            p.xaxis.axis_label = data_cols[0]

        # If Histogram should be plotted, calculate bins, aggregates and
        # averages:

        # Autocalculate bins if bins are not specified:
        if bins is None:
            values = df[data_cols].values
            values = values[~np.isnan(values)]
            data, bins = np.histogram(values)

        # Calculate bins if number of bins is given:
        elif isinstance(bins, int):
            if bins < 1:
                raise ValueError(
                    "<bins> can only be an integer>0, a list or a range of numbers."
                )
            values = df[data_cols].values
            values = values[~np.isnan(values)]
            v_min, v_max = values.min(), values.max()
            bins = np.linspace(v_min, v_max, bins + 1)

        if not isinstance(bins, str):
            bins = list(bins)

        if weights is not None:
            if weights not in df.columns:
                raise ValueError(
                    "Columns '%s' for <weights> is not in provided DataFrame."
                )
            else:
                weights = df[weights].values

        aggregates = []
        averages = []
        for col in data_cols:
            values = df[col].values
            if weights is not None:
                not_nan = ~(np.isnan(values) | np.isnan(weights))
                values_not_nan = values[not_nan]
                weights_not_nan = weights[not_nan]
                if sum(not_nan) < len(not_nan):
                    warnings.warn(
                        f"There are NaN values in column '{col}' or in the <weights> column. For the histogram, these rows have been neglected.",
                        Warning,
                    )
            else:
                not_nan = ~np.isnan(values)
                values_not_nan = values[not_nan]
                weights_not_nan = None
                if sum(not_nan) < len(not_nan):
                    warnings.warn(
                        f"There are NaN values in column '{col}'. For the histogram, these rows have been neglected.",
                        Warning,
                    )

            average = np.average(values_not_nan, weights=weights_not_nan)
            averages.append(average)

            data, bins = np.histogram(
                values_not_nan, bins=bins, weights=weights_not_nan
            )
            if normed:
                data = data / np.sum(data) * normed
            if cumulative:
                data = np.cumsum(data)
            aggregates.append(data)

        p = histogram(
            p,
            df,
            data_cols,
            colormap,
            aggregates,
            bins,
            averages,
            hovertool,
            hovertool_string,
            additional_columns,
            normed,
            cumulative,
            show_average,
            histogram_type,
            logy,
            **kwargs,
        )

    if kind == "area":

        p = areaplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            hovertool_string,
            xlabelname,
            figure_options["x_axis_type"],
            stacked,
            normed,
            **kwargs,
        )

    if kind == "pie":

        source["__x__values"] = x_old
        p = pieplot(
            source,
            data_cols,
            colormap,
            hovertool,
            hovertool_string,
            figure_options,
            xlabelname,
            **kwargs,
        )

    # Set xticks:
    if xticks is not None:
        p.xaxis[0].ticker = list(xticks)
    elif (xaxis_type == "numerical" and kind not in ["hist", "scatter"]) or (
        x_labels_dict is not None and kind != "barh"
    ):
        p.xaxis.ticker = x
    elif kind == "barh":
        p.yaxis.ticker = x
    if yticks is not None:
        p.yaxis.ticker = yticks

    # Format datetime ticks correctly:
    if figure_options["x_axis_type"] == "datetime":
        p.xaxis.formatter = DatetimeTickFormatter(
            milliseconds=["%H:%M:%S.%f"],
            seconds=["%H:%M:%S"],
            minutes=["%H:%M:%S"],
            hours=["%H:%M:%S"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )

    # Rotate xlabel if wanted:
    if vertical_xlabel:
        p.xaxis.major_label_orientation = np.pi / 2

    # Set panning option:
    if panning is False:
        p.toolbar.active_drag = None

    # Set zooming option:
    if zooming is False:
        p.toolbar.active_scroll = None

    # Set click policy for legend:
    if not stacked and kind != "pie":
        p.legend.click_policy = "hide"

    # Hide legend if wanted:
    if not legend:
        p.legend.visible = False

    # Modify legend position:
    else:
        if legend is True:
            p.legend.location = "top_right"
        elif legend in [
            "top_left",
            "top_center",
            "top_right",
            "center_left",
            "center",
            "center_right",
            "bottom_left",
            "bottom_center",
            "bottom_right",
        ]:
            p.legend.location = legend
        else:
            raise ValueError(
                "Legend can only be True/False or one of 'top_left', 'top_center', 'top_right', 'center_left', 'center', 'center_right', 'bottom_left', 'bottom_center', 'bottom_right'"
            )

    # Set fontsizes:
    set_fontsizes_of_figure(
        figure=p,
        fontsize_title=fontsize_title,
        fontsize_label=fontsize_label,
        fontsize_ticks=fontsize_ticks,
        fontsize_legend=fontsize_legend,
    )

    # Scientific formatting for axes:
    if disable_scientific_axes is None:
        pass
    elif disable_scientific_axes == "x":
        p.xaxis[0].formatter.use_scientific = False
    elif disable_scientific_axes == "y":
        p.yaxis[0].formatter.use_scientific = False
    elif disable_scientific_axes in ["xy", True]:
        p.xaxis[0].formatter.use_scientific = False
        p.yaxis[0].formatter.use_scientific = False
    else:
        raise ValueError(
            """Keyword parameter <disable_scientific_axes> only accepts "xy", True, "x", "y" or None."""
        )

    # If rangetool is used, add it to layout:
    if p_rangetool is not None:
        p = column(p, p_rangetool)

    # Display plot if wanted
    if show_figure:
        show(p)

    # Return as (embeddable) HTML if wanted:
    if return_html:
        return embedded_html(p)

    # Return plot:
    return p


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


def _base_lineplot(
    linetype,
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    xlabelname,
    x_axis_type,
    plot_data_points,
    plot_data_points_size,
    hovertool_string,
    number_format,
    rangetool,
    **kwargs,
):
    """Adds lineplot to figure p for each data_col."""

    p_rangetool = None
    # Add line (and optional scatter glyphs) to figure:
    linetype = getattr(p, linetype.lower())
    marker = kwargs.pop("marker", "circle")

    if rangetool:
        p_rangetool = _initialize_rangetool(p, x_axis_type, source)

    for name, color in zip(data_cols, colormap):
        glyph = linetype(
            x="__x__values",
            y=name,
            legend_label=" " + name,
            source=source,
            color=color,
            **kwargs,
        )

        if plot_data_points:
            p.scatter(
                x="__x__values",
                y=name,
                legend_label=" " + name,
                source=source,
                color=color,
                marker=marker,
                size=plot_data_points_size,
            )

        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if hovertool_string is None:
                if x_axis_type == "datetime":
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original{%F}"),
                        (name, "@{%s}%s" % (name, number_format)),
                    ]
                    my_hover.formatters = {"@__x__values_original": "datetime"}
                else:
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original"),
                        (name, "@{%s}%s" % (name, number_format)),
                    ]
            else:
                my_hover.tooltips = hovertool_string
            p.add_tools(my_hover)

        if rangetool:

            p_rangetool.line("__x__values", name, source=source, color=color)

    return p, p_rangetool


def lineplot(
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    xlabelname,
    x_axis_type,
    plot_data_points,
    plot_data_points_size,
    hovertool_string,
    number_format,
    rangetool,
    **kwargs,
):
    return _base_lineplot(
        linetype="line",
        p=p,
        source=source,
        data_cols=data_cols,
        colormap=colormap,
        hovertool=hovertool,
        xlabelname=xlabelname,
        x_axis_type=x_axis_type,
        plot_data_points=plot_data_points,
        plot_data_points_size=plot_data_points_size,
        hovertool_string=hovertool_string,
        number_format=number_format,
        rangetool=rangetool,
        **kwargs,
    )


def stepplot(
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    xlabelname,
    x_axis_type,
    plot_data_points,
    plot_data_points_size,
    hovertool_string,
    number_format,
    rangetool,
    **kwargs,
):
    return _base_lineplot(
        linetype="step",
        p=p,
        source=source,
        data_cols=data_cols,
        colormap=colormap,
        hovertool=hovertool,
        xlabelname=xlabelname,
        x_axis_type=x_axis_type,
        plot_data_points=plot_data_points,
        plot_data_points_size=plot_data_points_size,
        hovertool_string=hovertool_string,
        number_format=number_format,
        rangetool=rangetool,
        **kwargs,
    )


def pointplot(
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    hovertool_string,
    xlabelname,
    x_axis_type,
    number_format,
    **kwargs,
):
    """Adds pointplot to figure p for each data_col."""

    N_cols = len(data_cols)

    # Define marker for pointplot:
    if "marker" in kwargs:
        markers = [kwargs["marker"]] * N_cols
        del kwargs["marker"]
    else:
        marker = [
            "circle",
            "square",
            "triangle",
            "asterisk",
            "circle_x",
            "square_x",
            "inverted_triangle",
            "x",
            "circle_cross",
            "square_cross",
            "diamond",
            "cross",
        ]
        markers = marker * int(N_cols / 20 + 1)
        markers = markers[:N_cols]

    # Add scatter/point glyphs to figure:
    for name, color, marker in zip(data_cols, colormap, markers):

        glyph = p.scatter(
            x="__x__values",
            y=name,
            legend_label=" " + name,
            source=source,
            color=color,
            marker=marker,
            **kwargs,
        )
        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if hovertool_string is None:
                if x_axis_type == "datetime":
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original{%F}"),
                        (name, "@{%s}%s" % (name, number_format)),
                    ]
                    my_hover.formatters = {"@__x__values_original": "datetime"}
                else:
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original"),
                        (name, "@{%s}%s" % (name, number_format)),
                    ]
            else:
                my_hover.tooltips = hovertool_string
            p.add_tools(my_hover)

    return p


def scatterplot(  # noqa C901
    p,
    df,
    x,
    x_old,
    y,
    category,
    category_values,
    colormap,
    hovertool,
    hovertool_string,
    additional_columns,
    x_axis_type,
    xlabelname,
    ylabelname,
    **kwargs,
):
    """Adds a scatterplot to figure p for each data_col."""

    # Set standard size and linecolor of markers:
    if "size" not in kwargs:
        kwargs["size"] = 10
    if "line_color" not in kwargs:
        kwargs["line_color"] = "black"

    # Define source:
    source = ColumnDataSource({"__x__values": x, "__x__values_original": x_old, "y": y})
    for kwarg, value in kwargs.items():
        if value in df.columns:
            source.data[value] = df[value].values
    for add_col in additional_columns:
        source.data[add_col] = df[add_col].values

    # Define Colormapper for categorical scatterplot:
    if category is not None:

        category = str(category)
        source.data[category] = category_values

        # Make numerical categorical scatterplot:
        if check_type(category_values) == "numeric":

            kwargs["legend_label"] = category + " "

            # Define colormapper for numerical scatterplot:
            if colormap is None:
                colormap = Inferno256
            elif isinstance(colormap, str):
                if colormap in all_palettes:
                    colormap = all_palettes[colormap]
                    max_key = max(colormap.keys())
                    colormap = colormap[max_key]
                else:
                    raise ValueError(
                        f"Could not find <colormap> with name {colormap}. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): {list(all_palettes.keys())}"
                    )
            elif isinstance(colormap, (list, tuple)):
                pass
            else:
                raise ValueError(
                    "<colormap> can onyl be None, a name of a colorpalette as string( see https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ) or a list/tuple of colors."
                )

            colormapper = LinearColorMapper(palette=colormap)

            # Set fill-color to colormapper:
            kwargs["fill_color"] = {"field": category, "transform": colormapper}

            # Define Colorbar:
            colorbar_options = {
                "color_mapper": colormapper,
                "label_standoff": 0,
                "border_line_color": None,
                "location": (0, 0),
            }
            colorbar = ColorBar(**colorbar_options)
            p.add_layout(colorbar, "right")

            # Draw glyph:
            glyph = p.scatter(x="__x__values", y="y", source=source, **kwargs)

            # Add Hovertool
            if hovertool:
                my_hover = HoverTool(renderers=[glyph])
                if hovertool_string is None:
                    if x_axis_type == "datetime":
                        my_hover.tooltips = [
                            (xlabelname, "@__x__values_original{%F}"),
                            (ylabelname, "@y"),
                        ]
                        my_hover.formatters = {"@__x__values_original": "datetime"}
                    else:
                        my_hover.tooltips = [
                            (xlabelname, "@__x__values_original"),
                            (ylabelname, "@y"),
                        ]
                    my_hover.tooltips.append((str(category), "@{%s}" % category))
                else:
                    my_hover.tooltips = hovertool_string
                p.add_tools(my_hover)

        # Make categorical scatterplot:
        elif check_type(category_values) == "object":

            # Define colormapper for categorical scatterplot:
            labels, categories = pd.factorize(category_values)
            colormap = get_colormap(colormap, len(categories))

            # Draw each category as separate glyph:
            x, y = source.data["__x__values"], source.data["y"]
            for cat, color in zip(categories, colormap):

                # Define reduced source for this categorx:
                x_cat = x[category_values == cat]
                x_old_cat = x_old[category_values == cat]
                y_cat = y[category_values == cat]
                cat_cat = category_values[category_values == cat]
                source = ColumnDataSource(
                    {
                        "__x__values": x_cat,
                        "__x__values_original": x_old_cat,
                        "y": y_cat,
                        "category": cat_cat,
                    }
                )
                for kwarg, value in kwargs.items():
                    if value in df.columns:
                        source.data[value] = df[value].values[category_values == cat]
                for add_col in additional_columns:
                    source.data[add_col] = df[add_col].values[category_values == cat]

                # Draw glyph:
                glyph = p.scatter(
                    x="__x__values",
                    y="y",
                    legend_label=str(cat) + " ",
                    source=source,
                    color=color,
                    **kwargs,
                )

                # Add Hovertool
                if hovertool:
                    my_hover = HoverTool(renderers=[glyph])
                    if hovertool_string is None:
                        if x_axis_type == "datetime":
                            my_hover.tooltips = [
                                (xlabelname, "@__x__values_original{%F}"),
                                (ylabelname, "@y"),
                            ]
                            my_hover.formatters = {"@__x__values_original": "datetime"}
                        else:
                            my_hover.tooltips = [
                                (xlabelname, "@__x__values_original"),
                                (ylabelname, "@y"),
                            ]
                        my_hover.tooltips.append((str(category), "@category"))
                    else:
                        my_hover.tooltips = hovertool_string
                    p.add_tools(my_hover)

            if len(categories) > 5:
                warnings.warn(
                    "There are more than 5 categories in the scatterplot. The legend might be crowded, to hide the axis you can pass 'legend=False' as an optional argument."
                )

        else:
            raise ValueError(
                "<category> is not supported with datetime objects. Consider casting the datetime objects to strings, which can be used as <category> values."
            )

    # Draw non-categorical plot:
    else:
        # Draw glyph:
        glyph = p.scatter(
            x="__x__values", y="y", source=source, legend_label="Hide/Show", **kwargs
        )

        # Add Hovertool:
        if hovertool:
            my_hover = HoverTool(renderers=[glyph])
            if hovertool_string is None:
                if x_axis_type == "datetime":
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original{%F}"),
                        (ylabelname, "@y"),
                    ]
                    my_hover.formatters = {"@__x__values_original": "datetime"}
                else:
                    my_hover.tooltips = [
                        (xlabelname, "@__x__values_original"),
                        (ylabelname, "@y"),
                    ]
            else:
                my_hover.tooltips = hovertool_string
            p.add_tools(my_hover)

    return p


def histogram(
    p,
    df,
    data_cols,
    colormap,
    aggregates,
    bins,
    averages,
    hovertool,
    hovertool_string,
    additional_columns,
    normed,
    cumulative,
    show_average,
    histogram_type,
    logy,
    **kwargs,
):
    "Adds histogram to figure p for each data_col."

    bottom = None
    N_cols = len(data_cols)
    if logy:
        bottomvalue = 0.000000001
    else:
        bottomvalue = 0

    for i, name, color, aggregate, average in zip(
        range(len(data_cols)), data_cols, colormap, aggregates, averages
    ):

        if histogram_type is None:
            histogram_type = "topontop"

        if histogram_type not in ["sidebyside", "topontop", "stacked"]:
            raise ValueError(
                '<histogram_type> can only be one of ["sidebyside", "topontop", "stacked"].'
            )

        # Get bar edges to plot for side-by-side display
        if histogram_type == "sidebyside":
            left = [
                bins[index] + float(i) / N_cols * (bins[index + 1] - bins[index])
                for index in range(len(bins) - 1)
            ]
            right = [
                bins[index] + float(i + 1) / N_cols * (bins[index + 1] - bins[index])
                for index in range(len(bins) - 1)
            ]
            bottom = [bottomvalue] * len(left)
            top = aggregate

        # Get bar edges for top-on-top display:
        elif histogram_type == "topontop":
            left = bins[:-1]
            right = bins[1:]
            bottom = [bottomvalue] * len(left)
            top = aggregate
            if "alpha" not in kwargs:
                kwargs["alpha"] = 0.5

        # Get bar edges for stacked display:
        elif histogram_type == "stacked":
            left = bins[:-1]
            right = bins[1:]
            if bottom is None:
                bottom = [bottomvalue] * len(left)
                top = [0] * len(left)
            else:
                bottom = top
            top = top + aggregate

        # Define DataSource for plotting:
        source = ColumnDataSource(
            dict(
                bins=[
                    "%s－%s" % (bins[index], bins[index + 1])
                    for index in range(len(bins) - 1)
                ],
                left=left,
                right=right,
                top=top,
                bottom=bottom,
            )
        )

        # Add histogram glyphs to plot:
        g1 = p.quad(
            left="left",
            right="right",
            bottom="bottom",
            top="top",
            source=source,
            color=color,
            legend_label=name,
            **kwargs,
        )

        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[g1])
            if hovertool_string is None:
                my_hover.tooltips = (
                    f"<h3> {name}: </h3> <h4>bin=@bins</h4> <h4>value=@top </h4>"
                )
            else:
                warnings.warn(
                    "For histograms, <hovertool_string> is not a supported keyword argument."
                )
            p.add_tools(my_hover)

        # Plot average line if wanted:
        if show_average:

            for sign in [1, -1]:
                g1 = p.ray(
                    x=[average],
                    y=[0],
                    length=0,
                    angle=sign * np.pi / 2,
                    line_width=3,
                    color=color,
                    legend_label="<%s> = %f" % (name, average),
                )

    p.xaxis.ticker = bins

    return p


def areaplot(
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    hovertool_string,
    xlabelname,
    x_axis_type,
    stacked,
    normed,
    **kwargs,
):
    """Adds areaplot to figure p for each data_col."""

    # Transform columns to be able to plot areas as patches:
    if not stacked:
        line_source = deepcopy(source)
        for key in list(source.keys()):
            if key == "__x__values":
                source[key] = [source[key][0]] + list(source[key]) + [source[key][-1]]
            else:
                source[key] = np.array([0] + list(source[key]) + [0])
        if "alpha" not in kwargs:
            kwargs["alpha"] = 0.4
    else:
        if "alpha" not in kwargs:
            kwargs["alpha"] = 0.8
        if normed is not False:
            data = []
            for col in data_cols:
                data.append(source[col])
            data = np.array(data)
            norm = np.sum(data, axis=0)
            for col in data_cols:
                source[col] = np.array(source[col]) / norm * normed

        line_source = {
            "__x__values": source["__x__values"],
            "__x__values_original": source["__x__values_original"],
        }
        baseline = np.zeros(len(source["__x__values"]))
        del source["__x__values_original"]
        source["__x__values"] = (
            list(source["__x__values"]) + list(source["__x__values"])[::-1]
        )
        for j, col in enumerate(data_cols):

            # Stack lines:
            line_source[col + "_plot"] = baseline + np.array(source[col])
            line_source[col] = np.array(source[col])

            # Stack patches:
            source[col] = baseline + np.array(source[col])
            new_baseline = source[col]
            source[col] = list(source[col]) + list(baseline)[::-1]
            baseline = new_baseline

    # Add area patches to figure:
    for j, name, color in list(zip(range(len(data_cols)), data_cols, colormap))[::-1]:
        p.patch(
            x="__x__values",
            y=name,
            legend_label=" " + name,
            source=source,
            color=color,
            **kwargs,
        )

        # Add hovertool:
        if hovertool and int(len(data_cols) / 2) == j + 1:

            # Add single line for displaying hovertool:
            if stacked:
                y = name + "_plot"
            else:
                y = name
            glyph = p.line(
                x="__x__values",
                y=y,
                legend_label=" " + name,
                source=line_source,
                color=color,
                alpha=0,
            )

            # Define hovertool and add to line:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if hovertool_string is None:
                if x_axis_type == "datetime":
                    my_hover.tooltips = [(xlabelname, "@__x__values_original{%F}")] + [
                        (name, "@{%s}" % name) for name in data_cols[::-1]
                    ]
                    my_hover.formatters = {"@__x__values_original": "datetime"}
                else:
                    my_hover.tooltips = [(xlabelname, "@__x__values_original")] + [
                        (name, "@{%s}" % name) for name in data_cols[::-1]
                    ]
            else:
                my_hover.tooltips = hovertool_string
            p.add_tools(my_hover)

    return p


def pieplot(
    source,
    data_cols,
    colormap,
    hovertool,
    hovertool_string,
    figure_options,
    xlabelname,
    **kwargs,
):

    """Creates a Pieplot from the provided data."""

    # Determine Colormap for Pieplot:
    colormap = get_colormap(colormap, len(source["__x__values"]))
    source["color"] = colormap

    max_col_stringlength = max([len(col) for col in data_cols])

    # Create Figure for Pieplot:
    plot_width = figure_options["plot_width"]
    plot_height = figure_options["plot_height"]
    title = figure_options["title"]
    toolbar_location = None
    x_range = (-1.4 - 0.05 * max_col_stringlength, 2)
    y_range = (-1.2, 1.2)
    p = figure(
        plot_width=plot_width,
        plot_height=plot_height,
        title=title,
        toolbar_location=toolbar_location,
        x_range=x_range,
        y_range=y_range,
    )
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    # Calculate angles for Pieplot:
    for col in data_cols:
        source[col + "_angle"] = source[col] / source[col].sum() * 2 * np.pi

    # Make Pieplots:
    for i, col in list(enumerate(data_cols))[::-1]:
        inner_radius = float(i) / len(data_cols)
        outer_radius = float(i + 0.9) / len(data_cols)
        source["inner_radius"] = [inner_radius] * len(source["__x__values"])
        source["outer_radius"] = [outer_radius] * len(source["__x__values"])

        legend_parameter_name = "legend_field"
        if i == 0:
            kwargs[legend_parameter_name] = "__x__values_original"
            print(kwargs[legend_parameter_name])
        else:
            kwargs.pop(legend_parameter_name, None)

        if "line_color" not in kwargs:
            kwargs["line_color"] = "white"

        glyph = p.annular_wedge(
            x=0,
            y=0,
            inner_radius="inner_radius",
            outer_radius="outer_radius",
            start_angle=cumsum(col + "_angle", include_zero=True),
            end_angle=cumsum(col + "_angle"),
            fill_color="color",
            source=source,
            **kwargs,
        )

        # Add annotation:
        if len(data_cols) > 1:
            text_source = {
                "__x__values": [-1.3 - 0.05 * max_col_stringlength],
                "y": [0.5 - 0.3 * i],
                "text": [col],
            }
            p.text(
                x="__x__values",
                y="y",
                text="text",
                text_font_style="bold",
                source=text_source,
            )

            p.line(
                x=[-1.3 - 0.04 * (max_col_stringlength - len(col)), 0],
                y=[0.5 - 0.3 * i, -(inner_radius + outer_radius) / 2],
                line_color="black",
            )

        # Define hovertool and add to Pieplot:
        if hovertool:
            my_hover = HoverTool(renderers=[glyph])
            if hovertool_string is None:
                my_hover.tooltips = [
                    (xlabelname, "@__x__values_original"),
                    (col, "@{%s}" % col),
                ]
            else:
                my_hover.tooltips = hovertool_string
            p.add_tools(my_hover)

    return p


def mapplot(df, x, y, **kwargs):
    # Get data of x and y columns:
    if x not in df.columns:
        raise ValueError(
            "<x> parameter has to be a column name of the provided dataframe."
        )
    if y not in df.columns:
        raise ValueError(
            "<y> parameter has to be a column name of the provided dataframe."
        )
    latitude = df[y]
    longitude = df[x]

    # Check if NaN values are in x & y columns:
    if (pd.isnull(latitude).sum() > 0) or (pd.isnull(longitude).sum() > 0):
        raise ValueError(
            "There are NaN values in the <x> or <y> column. The map plot API of Pandas Bokeh does not support this. Please drop the NaN rows for plotting."
        )

    # Check values of longitude and latitude:
    if not (check_type(latitude) == "numeric" and check_type(longitude) == "numeric"):
        raise ValueError(
            "<x> and <y> have to be numeric columns of the DataFrame. Further they correspond to longitude, latitude in WGS84 projection."
        )
    if not (np.min(latitude) > -90 and np.max(latitude) < 90):
        raise ValueError(
            "All values of the y-column have to be restricted to (-90, 90). The <y> value corresponds to the latitude in WGS84 projection."
        )
    if not (np.min(longitude) > -180 and np.max(longitude) < 180):
        raise ValueError(
            "All values of the x-column have to be restricted to (-180, 180). The <x> value corresponds to the longitude in WGS84 projection."
        )

    # Convert longitude & latitude coordinates to Web Mercator projection:
    if "x" in df.columns or "y" in df.columns:
        raise ValueError(
            "The map plot API overrides the columns named 'x' and 'y' with the coordinates for plotting. Please rename your columns 'x' and 'y'."
        )

    RADIUS = 6378137.0
    df["y"] = np.log(np.tan(np.pi / 4 + np.radians(latitude) / 2)) * RADIUS
    df["x"] = np.radians(longitude) * RADIUS

    return geoplot(df, **kwargs)


##############################################################################
###########Class to add Bokeh plotting methods to Pandas DataFrame
##############################################################################


class BasePlotMethods(PandasObject):
    def __init__(self, data):
        self._parent = data  # can be Series or DataFrame

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class FramePlotMethods(BasePlotMethods):
    """DataFrame plotting accessor and method

    Examples
    --------
    >>> df.plot_bokeh.line()
    >>> df.plot_bokeh.scatter('x', 'y')
    >>> df.plot_bokeh.hexbin()

    These plotting methods can also be accessed by calling the accessor as a
    method with the ``kind`` argument:
    ``df.plot_bokeh(kind='line')`` is equivalent to ``df.plot_bokeh.line()``
    """

    def __call__(self, *args, **kwargs):
        return plot(self.df, *args, **kwargs)

    @property
    def df(self):

        dataframe = self._parent

        # Convert PySpark Dataframe to Pandas Dataframe:
        if hasattr(dataframe, "toPandas"):
            dataframe = dataframe.toPandas()

        return dataframe

    __call__.__doc__ = plot.__doc__

    def line(self, x=None, y=None, **kwargs):
        """
        Plot DataFrame columns as lines.

        This function is useful to plot lines using DataFrame's values
        as coordinates.

        Parameters
        ----------
        x : int or str, optional
            Columns to use for the horizontal axis.
            Either the location or the label of the columns to be used.
            By default, it will use the DataFrame indices.
        y : int, str, or list of them, optional
            The values to be plotted.
            Either the location or the label of the columns to be used.
            By default, it will use the remaining DataFrame numeric columns.
        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------

        Bokeh.plotting.figure or Bokeh.layouts.row

        Examples
        --------

        .. plot::
            :context: close-figs

            The following example shows the populations for some animals
            over the years.

            >>> df = pd.DataFrame({
            ...    'pig': [20, 18, 489, 675, 1776],
            ...    'horse': [4, 25, 281, 600, 1900]
            ...    }, index=[1990, 1997, 2003, 2009, 2014])
            >>> lines = df.plot_bokeh.line()


        .. plot::
            :context: close-figs

            The following example shows the relationship between both
            populations.

            >>> lines = df.plot_bokeh.line(x='pig', y='horse')
        """
        return self(kind="line", x=x, y=y, **kwargs)

    def step(self, x=None, y=None, **kwargs):
        """
        Plot DataFrame columns as step lines.

        This function is useful to plot step lines using DataFrame's values
        as coordinates.

        Parameters
        ----------
        x : int or str, optional
            Columns to use for the horizontal axis.
            Either the location or the label of the columns to be used.
            By default, it will use the DataFrame indices.
        y : int, str, or list of them, optional
            The values to be plotted.
            Either the location or the label of the columns to be used.
            By default, it will use the remaining DataFrame numeric columns.
        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------

        Bokeh.plotting.figure or Bokeh.layouts.row

        Examples
        --------

        .. plot::
            :context: close-figs

            The following example shows the populations for some animals
            over the years.

            >>> df = pd.DataFrame({
            ...    'pig': [20, 18, 489, 675, 1776],
            ...    'horse': [4, 25, 281, 600, 1900]
            ...    }, index=[1990, 1997, 2003, 2009, 2014])
            >>> steps = df.plot_bokeh.step()


        .. plot::
            :context: close-figs

            The following example shows the relationship between both
            populations.

            >>> steps = df.plot_bokeh.step(x='pig', y='horse')
        """
        return self(kind="step", x=x, y=y, **kwargs)

    def point(self, x=None, y=None, **kwargs):
        """
        Plot DataFrame columns as points.

        This function is useful to plot lines using DataFrame's values
        as coordinates.

        Parameters
        ----------
        x : int or str, optional
            Columns to use for the horizontal axis.
            Either the location or the label of the columns to be used.
            By default, it will use the DataFrame indices.
        y : int, str, or list of them, optional
            The values to be plotted.
            Either the location or the label of the columns to be used.
            By default, it will use the remaining DataFrame numeric columns.
        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------

        Bokeh.plotting.figure or Bokeh.layouts.row

        Examples
        --------

        .. plot::
            :context: close-figs

            The following example shows the populations for some animals
            over the years.

            >>> df = pd.DataFrame({
            ...    'pig': [20, 18, 489, 675, 1776],
            ...    'horse': [4, 25, 281, 600, 1900]
            ...    }, index=[1990, 1997, 2003, 2009, 2014])
            >>> lines = df.plot_bokeh.point()


        .. plot::
            :context: close-figs

            The following example shows the relationship between both
            populations.

            >>> lines = df.plot_bokeh.point(x='pig', y='horse')
        """
        return self(kind="point", x=x, y=y, **kwargs)

    def bar(self, x=None, y=None, **kwds):
        """
        Vertical bar plot.

        A bar plot is a plot that presents categorical data with
        rectangular bars with lengths proportional to the values that they
        represent. A bar plot shows comparisons among discrete categories. One
        axis of the plot shows the specific categories being compared, and the
        other axis represents a measured value.

        Parameters
        ----------
        x : label or position, optional
            Allows plotting of one column versus another. If not specified,
            the index of the DataFrame is used.
        y : label or position, optional
            Allows plotting of one column versus another. If not specified,
            all numerical columns are used.
        **kwds
            Additional keyword arguments are documented in
            :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        pandas.DataFrame.plot_bokeh.barh : Horizontal bar plot.
        pandas.DataFrame.plot_bokeh : Make interactive plots of a DataFrame.

        Examples
        --------
        Basic plot.

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame({'lab':['A', 'B', 'C'], 'val':[10, 30, 20]})
            >>> ax = df.plot.bar(x='lab', y='val', rot=0)

        Plot a whole dataframe to a bar plot. Each column is assigned a
        distinct color, and each row is nested in a group along the
        horizontal axis.

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot.bar(rot=0)

        Instead of nesting, the figure can be split by column with
        ``subplots=True``. In this case, a :class:`numpy.ndarray` of
        :class:`matplotlib.axes.Axes` are returned.

        .. plot::
            :context: close-figs

            >>> axes = df.plot.bar(rot=0, subplots=True)
            >>> axes[1].legend(loc=2)  # doctest: +SKIP

        Plot a single column.

        .. plot::
            :context: close-figs

            >>> ax = df.plot.bar(y='speed', rot=0)

        Plot only selected categories for the DataFrame.

        .. plot::
            :context: close-figs

            >>> ax = df.plot.bar(x='lifespan', rot=0)
        """
        return self(kind="bar", x=x, y=y, **kwds)

    def barh(self, x=None, y=None, **kwds):
        """
        Make a horizontal bar plot.

        A horizontal bar plot is a plot that presents quantitative data with
        rectangular bars with lengths proportional to the values that they
        represent. A bar plot shows comparisons among discrete categories. One
        axis of the plot shows the specific categories being compared, and the
        other axis represents a measured value.

        Parameters
        ----------
        x : label or position, default DataFrame.index
            Column to be used for categories.
        y : label or position, default All numeric columns in dataframe
            Columns to be plotted from the DataFrame.
        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        pandas.DataFrame.plot_bokeh.bar: Vertical bar plot.
        pandas.DataFrame.plot_bokeh : Make plots of DataFrame using matplotlib.
        matplotlib.axes.Axes.bar : Plot a vertical bar plot using matplotlib.

        Examples
        --------
        Basic example

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame({'lab':['A', 'B', 'C'], 'val':[10, 30, 20]})
            >>> ax = df.plot_bokeh.barh(x='lab', y='val')

        Plot a whole DataFrame to a horizontal bar plot

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot_bokeh.barh()

        Plot a column of the DataFrame to a horizontal bar plot

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot_bokeh.barh(y='speed')

        Plot DataFrame versus the desired column

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot_bokeh.barh(x='lifespan')
        """
        return self(kind="barh", x=x, y=y, **kwds)

    def box(self, by=None, **kwds):
        r"""
        Make a box plot of the DataFrame columns.

        A box plot is a method for graphically depicting groups of numerical
        data through their quartiles.
        The box extends from the Q1 to Q3 quartile values of the data,
        with a line at the median (Q2). The whiskers extend from the edges
        of box to show the range of the data. The position of the whiskers
        is set by default to 1.5*IQR (IQR = Q3 - Q1) from the edges of the
        box. Outlier points are those past the end of the whiskers.

        For further details see Wikipedia's
        entry for `boxplot <https://en.wikipedia.org/wiki/Box_plot>`__.

        A consideration when using this chart is that the box and the whiskers
        can overlap, which is very common when plotting small sets of data.

        Parameters
        ----------
        by : string or sequence
            Column in the DataFrame to group by.
        **kwds : optional
            Additional keywords are documented in
            :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        pandas.Series.plot_bokeh.box: Draw a box plot from a Series object.

        Examples
        --------
        Draw a box plot from a DataFrame with four columns of randomly
        generated data.

        .. plot::
            :context: close-figs

            >>> data = np.random.randn(25, 4)
            >>> df = pd.DataFrame(data, columns=list('ABCD'))
            >>> ax = df.plot.box()
        """
        return self(kind="box", by=by, **kwds)

    def hist(self, **kwds):
        """
        Draw one histogram of the DataFrame's columns.

        A histogram is a representation of the distribution of data.
        This function groups the values of all given Series in the DataFrame
        into bins and draws all bins in one figure.
        This is useful when the DataFrame's Series are in a similar scale.

        Parameters
        ----------
        ...
        bins : int, default 10
            Number of histogram bins to be used.
        **kwds
            Additional keyword arguments are documented in
            :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        DataFrame.hist : Draw histograms per DataFrame's Series.
        Series.hist : Draw a histogram with Series' data.

        Examples
        --------
        When we draw a dice 6000 times, we expect to get each value around 1000
        times. But when we draw two dices and sum the result, the distribution
        is going to be quite different. A histogram illustrates those
        distributions.

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame(
            ...     np.random.randint(1, 7, 6000),
            ...     columns = ['one'])
            >>> df['two'] = df['one'] + np.random.randint(1, 7, 6000)
            >>> ax = df.plot_bokeh.hist(bins=12, alpha=0.5)
        """
        return self(kind="hist", **kwds)

    def area(self, x=None, y=None, **kwds):
        """
        Area plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        `**kwds` : optional
            Additional keyword arguments are documented in
            :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure
        """
        return self(kind="area", x=x, y=y, **kwds)

    def pie(self, y=None, **kwds):
        """
        Generate a pie plot.

        A pie plot is a proportional representation of the numerical data in a
        column. This function wraps :meth:`matplotlib.pyplot.pie` for the
        specified column. If no column reference is passed and
        ``subplots=True`` a pie plot is drawn for each numerical column
        independently.

        Parameters
        ----------
        y : int or label, optional
            Label or position of the column(s) to plot.
        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        Series.plot.pie : Generate a pie plot for a Series.
        DataFrame.plot : Make plots of a DataFrame.

        Examples
        --------
        In the example below we have a DataFrame with the information about
        planet's mass and radius. We pass the the 'mass' column to the
        pie function to get a pie plot.

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame({'mass': [0.330, 4.87 , 5.97],
            ...                    'radius': [2439.7, 6051.8, 6378.1]},
            ...                   index=['Mercury', 'Venus', 'Earth'])
            >>> plot = df.plot_bokeh.pie(y='mass')

        When you pass multiple y-columns, the plot contains several nested
        pieplots:

        .. plot::
            :context: close-figs

            >>> plot = df.plot.pie()

        """
        return self(kind="pie", y=y, **kwds)

    def scatter(self, x, y, category=None, **kwds):
        """
        Create a scatter plot with varying marker color.

        The coordinates of each point are defined by two dataframe columns and
        filled circles are used to represent each point. This kind of plot is
        useful to see complex correlations between two variables. Points could
        be for instance natural 2D coordinates like longitude and latitude in
        a map or, in general, any pair of metrics that can be plotted against
        each other.

        Parameters
        ----------
        x : int or str
            The column name or column position to be used as horizontal
            coordinates for each point.

        y : int or str
            The column name or column position to be used as vertical
            coordinates for each point.

        category : str or object
            A column name whose values will be used to color the
            marker points according to a colormap.

        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure or Bokeh.layouts.row

        See Also
        --------
        bokeh.plotting.figure.scatter : scatter plot using multiple input data
            formats.

        Examples
        --------
        Let's see how to draw a scatter plot using coordinates from the values
        in a DataFrame's columns.

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame([[5.1, 3.5, 0], [4.9, 3.0, 0], [7.0, 3.2, 1],
            ...                    [6.4, 3.2, 1], [5.9, 3.0, 2]],
            ...                   columns=['length', 'width', 'species'])
            >>> ax1 = df.plot_bokeh.scatter(x='length',
            ...                         y='width')

        And now with the color and size determined by a column as well.

        .. plot::
            :context: close-figs

            >>> ax2 = df.plot_bokeh.scatter(x='length',
            ...                       y='width',
            ...                       category='species',
            ...                       size="species",
            ...                       colormap='viridis')
        """
        return self(kind="scatter", x=x, y=y, category=category, **kwds)

    def map(self, x, y, **kwds):
        """
        Create a plot of geographic points stored in a Pandas DataFrame on an
        interactive map.

        The coordinates (latitude/longitude) of each point are defined by two
        dataframe columns.

        Parameters
        ----------
        x : int or str
            The column name or column position to be used as horizontal
            coordinates (longitude) for each point.

        y : int or str
            The column name or column position to be used as vertical
            coordinates (latitude) for each point.

        hovertool_string : str
            If specified, this string will be used for the hovertool (@{column}
            will be replaced by the value of the column for the element the
            mouse hovers over, see also Bokeh documentation). This can be
            used to display additional information on the map.

        tile_provider : None or str (default: 'CARTODBPOSITRON_RETINA')
            Define build-in tile provider for background maps. Possible
            values: None, 'CARTODBPOSITRON', 'CARTODBPOSITRON_RETINA',
            'STAMEN_TERRAIN', 'STAMEN_TERRAIN_RETINA', 'STAMEN_TONER',
            'STAMEN_TONER_BACKGROUND', 'STAMEN_TONER_LABELS'.

        tile_provider_url : str
            An arbitraty tile_provider_url of the form '/{Z}/{X}/{Y}*.png'
            can be passed to be used as background map.

        tile_attribution : str
            String (also HTML accepted) for showing attribution
            for tile source in the lower right corner.

        tile_alpha : float (Default: 1)
            Sets the alpha value of the background tile between [0, 1].

        **kwds
            Keyword arguments to pass on to :meth:`pandas.DataFrame.plot_bokeh`.

        Returns
        -------
        Bokeh.plotting.figure

        See Also
        --------
        bokeh.plotting.figure.scatter : scatter plot using multiple input data
            formats.

        Examples
        --------
        Let's see how to draw a scatter plot using coordinates from the values
        in a DataFrame's columns. Below an example of plotting all cities
        for more than 1 million inhabitants:

        .. plot::
            :context: close-figs

            >>> df_mapplot = pd.read_csv(r"https://raw.githubusercontent.com\
            ... /PatrikHlobil/Pandas-Bokeh/master/docs/Testdata\
            ... /populated%20places/populated_places.csv")
            >>> df_mapplot["size"] = df_mapplot["pop_max"] / 1000000
            >>> df_mapplot.plot_bokeh.map(
            ...     x="longitude",
            ...     y="latitude",
            ...     hovertool_string="<h2> @{name} </h2> \n\n \
            ...                       <h3> Population: @{pop_max} </h3>",
            ...     tile_provider='STAMEN_TERRAIN_RETINA',
            ...     size="size",
            ...     figsize=(900, 600),
            ...     title="World cities with more than 1.000.000 inhabitants")

        """
        return self(kind="map", x=x, y=y, **kwds)


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
