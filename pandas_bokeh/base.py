#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import numbers
import warnings
from copy import deepcopy

from bokeh.plotting import figure, show
import bokeh.plotting
import pandas as pd
import numpy as np
from bokeh.models import (
    HoverTool,
    ColumnDataSource,
    DatetimeTickFormatter,
    LinearColorMapper,
    LogColorMapper,
    CategoricalColorMapper,
    ColorBar,
)
from bokeh.models.tickers import FixedTicker, AdaptiveTicker
from bokeh.palettes import all_palettes, Inferno256
from bokeh.layouts import gridplot
from bokeh.models.ranges import FactorRange
from bokeh.transform import dodge, cumsum
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.core.properties import value
from bokeh.models.glyphs import Text
from bokeh.models.callbacks import CustomJS
from bokeh.events import Tap

from pandas.plotting._core import BasePlotMethods


def plot_grid(children, show_plot=True, return_html=False, **kwargs):
    """Create a grid of plots rendered on separate canvases and shows the layout. 
    plot_grid is designed to layout a set of plots. 

    ---------------------------------------------------------------
    Parameters:     

    -children (list of lists of Plot) – An array
        of plots to display in a grid, given as a list of lists of Plot objects. To
        leave a position in the grid empty, pass None for that position in the children
        list. OR list of Plot if called with ncols. OR an instance of GridSpec.
    - show_plot (bool, default=True) - Show the plot grid when function gets called
    - sizing_mode ("fixed", "stretch_both", "scale_width", "scale_height",
        "scale_both") – How will the items in the layout resize to fill the available
        space. Default is "fixed". For more information on the different modes see
        sizing_mode description on LayoutDOM. 
    - toolbar_location (above, below, left,
        right) – Where the toolbar will be located, with respect to the grid. Default is
        above. If set to None, no toolbar will be attached to the grid. 
    -ncols (int, optional) – Specify the number of columns you would like in your grid. 
        You must only pass an un-nested list of plots (as opposed to a list of lists of 
        plots) when using ncols. 
    - plot_width (int, optional) – The width you would like all your
        plots to be 
    - plot_height (int, optional) – The height you would like all your
        plots to be. 
    - toolbar_options (dict, optional) – A dictionary of options that
        will be used to construct the grid’s toolbar (an instance of ToolbarBox). If
        none is supplied, ToolbarBox’s defaults will be used. 
    - merge_tools (True, False) – Combine tools from all child plots into a single 
        toolbar. 

    -------------------------------------------------------------------        
    Returns: 

        A row or column containing the grid toolbar and the grid of plots
        (depending on whether the toolbar is left/right or above/below). 
        The grid is always a Column of Rows of plots."""

    layout = gridplot(children=children, **kwargs)

    if show_plot:
        show(layout)

    if return_html:
        return embedded_html(layout)

    return layout


def output_notebook(**kwargs):
    """Set the output of Bokeh to the current notebook.

    Parameters:
    ----------------------------------------------------------------	
    resources (Resource, optional) – How and where to load BokehJS from (default: CDN)
    verbose (bool, optional) – whether to display detailed BokehJS banner (default: False)
    hide_banner (bool, optional) – whether to hide the Bokeh banner (default: False)
    load_timeout (int, optional) – Timeout in milliseconds when plots assume load 
                                   timed out (default: 5000)
    notebook_type (string, optional) – Notebook type (default: jupyter)

    Returns:
    ----------------------------------------------------------------	
    None"""
    bokeh.plotting.reset_output()
    bokeh.plotting.output_notebook(**kwargs)


def output_file(filename, title="Bokeh Plot", mode="cdn", root_dir=None):
    """Set the output of Bokeh to the the provided filename.

    Parameters:	
    ----------------------------------------------------------------
    filename (str) – a filename for saving the HTML document
    title (str, optional) – a title for the HTML document (default: “Bokeh Plot”)
    mode (str, optional) – how to include BokehJS (default: 'cdn') One of: 'inline', 
                          'cdn', 'relative(-dev)' or 'absolute(-dev)'. See 
                          bokeh.resources.Resources for more details.
    root_dir (str, optional) – root directory to use for ‘absolute’ resources. 
                              (default: None) This value is ignored for other 
                              resource types, e.g. INLINE or CDN.

    Returns:	
    ----------------------------------------------------------------
    None"""
    bokeh.plotting.reset_output()
    bokeh.plotting.output_file(filename, title=title, mode=mode, root_dir=root_dir)


def embedded_html(fig):
    """Returns an html string that contains all neccessary CSS&JS files, 
    together with the div containing the Bokeh plot. As input, a figure fig
    is expected."""

    # Pack CDN resources:
    html_embedded = ""
    for css in CDN.css_files:
        html_embedded += (
            """<link
        href="%s"
        rel="stylesheet" type="text/css">
    """
            % css
        )

    for js in CDN.js_files:
        html_embedded += (
            """<script src="%s"></script>
    """
            % js
        )

    # Add plot script and div
    script, div = components(fig)
    html_embedded += "\n\n" + script + "\n\n" + div

    return html_embedded


def check_type(data):
    """Checks type of provided data array."""

    if isinstance(data[0], numbers.Number):
        return "numeric"
    elif isinstance(data[0], (np.datetime64, datetime.datetime, datetime.date)):
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
                "Could not find <colormap> with name %s. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): %s"
                % (colormap, list(all_palettes.keys()))
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


def plot(
    df_in,
    x=None,
    y=None,
    kind="line",
    figsize=None,
    use_index=True,
    title="",
    grid=None,  # TODO:
    legend="top_right",
    logx=False,
    logy=False,
    xlabel=None,
    ylabel=None,
    xticks=None,
    yticks=None,
    xlim=None,
    ylim=None,
    fontsize=None,  # TODO:
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
    show_figure=True,
    return_html=False,
    panning=True,
    zooming=True,
    toolbar_location="right",
    hovertool=True,
    vertical_xlabel=False,
    webgl=True,
    **kwargs
):
    # TODO: Make docstring
    """Method for creating a interactive with 'Bokeh' as plotting backend. Available
    plot kinds are:

    * line
    * point
    * scatter
    * bar
    * histogram

    Examples
    --------
    >>> df.plot_bokeh.line()
    >>> df.plot_bokeh.scatter(x='x',y='y')
    
    These plotting methods can also be accessed by calling the accessor as a
    method with the ``kind`` argument:
    ``df.plot_bokeh(kind='line')`` is equivalent to ``df.plot_bokeh.line()``

    For more informations about the individual plot kind implementations, have a
    look at the underlying methods (like df.plot_bokeh.line) or visit
    https://github.com/PatrikHlobil/Pandas-Bokeh. 
    
    """

    # Make a local copy of the DataFrame:
    df = df_in.copy()
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    # Get and check options for base figure:
    figure_options = {
        "title": title,
        "toolbar_location": toolbar_location,
        "active_scroll": "wheel_zoom",
        "plot_width": 600,
        "plot_height": 400,
        "output_backend": "webgl",
    }
    if not figsize is None:
        width, height = figsize
        figure_options["plot_width"] = width
        figure_options["plot_height"] = height
    if logx:
        figure_options["x_axis_type"] = "log"
    if logy:
        figure_options["y_axis_type"] = "log"
    if not xlabel is None:
        figure_options["x_axis_label"] = xlabel
    if not ylabel is None:
        figure_options["y_axis_label"] = ylabel
    if not xlim is None:
        if not isinstance(xlim, (tuple, list)):
            raise ValueError("<xlim> must be a list/tuple of form (x_min, x_max).")
        elif len(xlim) != 2:
            raise ValueError("<xlim> must be a list/tuple of form (x_min, x_max).")
        else:
            figure_options["x_range"] = xlim
    if not ylim is None:
        if not isinstance(ylim, (tuple, list)):
            raise ValueError("<ylim> must be a list/tuple of form (y_min, y_max).")
        elif len(ylim) != 2:
            raise ValueError("<ylim> must be a list/tuple of form (y_min, y_max).")
        else:
            figure_options["y_range"] = ylim
    if webgl:
        figure_options["output_backend"] = "webgl"

    # Set standard linewidth:
    if "line_width" not in kwargs:
        kwargs["line_width"] = 2

    # Get x-axis Name and Values:
    delete_in_y = None
    if not x is None:
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
            if not df.index.name is None:
                name = str(df.index.name)
            else:
                name = ""
        else:
            x = np.linspace(0, len(df) - 1, len(df))
            name = ""

    if kind == "barh":
        if "y_axis_label" not in figure_options:
            figure_options["y_axis_label"] = name
    elif "x_axis_label" not in figure_options:
        figure_options["x_axis_label"] = name

    # Check type of x-axis:
    if check_type(x) == "datetime":
        figure_options["x_axis_type"] = "datetime"
        xaxis_type = "datetime"
        if not xlim is None:
            starttime, endtime = xlim
            try:
                starttime = pd.to_datetime(starttime)
            except:
                raise ValueError("Could not parse x_min input of <xlim> as datetime.")
            try:
                endtime = pd.to_datetime(endtime)
            except:
                raise ValueError("Could not parse x_max input of <xlim> as datetime.")
            figure_options["x_range"] = (starttime, endtime)

    elif check_type(x) == "numeric":
        xaxis_type = "numerical"
    else:
        xaxis_type = "categorical"

    if kind in ["bar", "barh", "pie"]:
        xaxis_type = "categorical"

    if xaxis_type == "categorical":
        if check_type(x) == "datetime":
            x = _times_to_string(x)
        else:
            x = [str(el) for el in x]
        if kind != "hist":
            figure_options["x_range"] = x
        if "x_axis_type" in figure_options:
            del figure_options["x_axis_type"]

    # Determine data cols to plot (only plot numeric data):
    if y is None:
        cols = df.columns
    elif not isinstance(y, (list, tuple)):
        cols = [y]
    else:
        cols = y
    data_cols = []
    for i, col in enumerate(cols):
        if col not in df.columns:
            raise Exception(
                "Could not find '%s' in the columns of the provided DataFrame/Series. Please provide for the <y> parameter either a column name of the DataFrame/Series or an array of the same length."
                % col
            )
        if np.issubdtype(df[col].dtype, np.number):
            data_cols.append(col)
    N_cols = len(data_cols)
    if N_cols == 0:
        raise Exception("No numeric data columns found for plotting.")

    # Convert y-column names into string representation:
    df.rename(columns={col: str(col) for col in data_cols}, inplace=True)
    data_cols = [str(col) for col in data_cols]

    # Delete x column if it appears in y columns:
    if not delete_in_y is None:
        if delete_in_y in data_cols:
            data_cols.remove(delete_in_y)

    # Create Figure for plotting:
    p = figure(**figure_options)
    if "x_axis_type" not in figure_options:
        figure_options["x_axis_type"] = None

    # Define xlabel name as "x" if no label is provided by user or data:
    xlabelname = (
        figure_options["x_axis_label"]
        if figure_options.get("x_axis_label", "") != ""
        else "x"
    )

    # Define ColumnDataSource for Plot if kind != "hist":
    if kind != "hist":
        source = {col: df[col].values for col in data_cols}
        source["x"] = x

    # Define colormap
    if kind not in ["scatter", "pie"]:
        colormap = get_colormap(colormap, N_cols)

    if not color is None:
        colormap = get_colormap([color], N_cols)

    # Add Glyphs to Plot:
    if kind == "line":
        p = lineplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            xlabelname,
            figure_options["x_axis_type"],
            plot_data_points,
            plot_data_points_size,
            **kwargs
        )

    if kind == "point":
        p = pointplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            xlabelname,
            figure_options["x_axis_type"],
            **kwargs
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

        # Get values for categorical colormap:
        category_values = None
        if category in df.columns:
            category_values = df[category].values
        elif not category is None:
            raise Exception(
                "<category> parameter has to be either None or the name of a single column of the DataFrame"
            )

        scatterplot(
            p,
            x,
            y,
            category,
            category_values,
            colormap,
            hovertool,
            x_axis_type=figure_options["x_axis_type"],
            xlabelname=xlabelname,
            ylabelname=y_column,
            **kwargs
        )

    if kind == "bar" or kind == "barh":

        # Define data source for barplot:
        data = {col: df[col].values for col in data_cols}
        data["x"] = x
        source = ColumnDataSource(data)

        # Create Figure (just for categorical barplots):
        del figure_options["x_axis_type"]
        del figure_options["x_range"]
        if kind == "bar":
            figure_options["x_range"] = list(x)
        elif kind == "barh":
            figure_options["y_range"] = list(x)
            if "y_axis_label" not in figure_options:
                figure_options["y_axis_label"] = xlabelname
        p = figure(**figure_options)
        figure_options["x_axis_type"] = None

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
                        x=dodge("x", shift, range=p.x_range),
                        top=name,
                        width=width,
                        source=source,
                        color=color,
                        legend=" " + name,
                        **kwargs
                    )
                    hovermode = "vline"

                elif kind == "barh":
                    glyph = p.hbar(
                        y=dodge("x", shift, range=p.y_range),
                        right=name,
                        height=width,
                        source=source,
                        color=color,
                        legend=" " + name,
                        **kwargs
                    )
                    hovermode = "hline"

                if hovertool:
                    my_hover = HoverTool(mode=hovermode, renderers=[glyph])
                    my_hover.tooltips = [(xlabelname, "@x"), (name, "@{%s}" % name)]
                    p.add_tools(my_hover)

        if stacked:

            if kind == "bar":
                glyph = p.vbar_stack(
                    data_cols,
                    x="x",
                    width=0.8,
                    source=source,
                    color=colormap,
                    legend=[value(col) for col in data_cols],
                    **kwargs
                )
                hovermode = "vline"

            elif kind == "barh":
                glyph = p.hbar_stack(
                    data_cols,
                    y="x",
                    height=0.8,
                    source=source,
                    color=colormap,
                    legend=[value(col) for col in data_cols],
                    **kwargs
                )
                hovermode = "hline"

            if hovertool:
                my_hover = HoverTool(mode=hovermode, renderers=[glyph[-1]])
                my_hover.tooltips = [(xlabelname, "@x")] + [
                    (col, "@%s" % col) for col in data_cols
                ]
                p.add_tools(my_hover)

    if kind == "hist":

        # Disable line_color (for borders of histogram bins) per default:
        if not "line_color" in kwargs:
            kwargs["line_color"] = None
        elif kwargs["line_color"] == True:
            del kwargs["line_color"]

        # Check for stacked keyword:
        if stacked and histogram_type not in [None, "stacked"]:
            warnings.warn(
                "<histogram_type> was set to '%s', but was overriden by <stacked>=True parameter."
                % histogram_type
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

        bins = list(bins)

        if not weights is None:
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
            if not weights is None:
                not_nan = ~(np.isnan(values) | np.isnan(weights))
                values_not_nan = values[not_nan]
                weights_not_nan = weights[not_nan]
                if sum(not_nan) < len(not_nan):
                    warnings.warn(
                        "There are NaN values in column '%s' or in the <weights> column. For the histogram, these rows have been neglected."
                        % col,
                        Warning,
                    )
            else:
                not_nan = ~np.isnan(values)
                values_not_nan = values[not_nan]
                weights_not_nan = None
                if sum(not_nan) < len(not_nan):
                    warnings.warn(
                        "There are NaN values in column '%s'. For the histogram, these rows have been neglected."
                        % col,
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
            data_cols,
            colormap,
            aggregates,
            bins,
            averages,
            hovertool,
            normed,
            cumulative,
            show_average,
            histogram_type,
            logy,
            **kwargs
        )

    if kind == "area":

        p = areaplot(
            p,
            source,
            data_cols,
            colormap,
            hovertool,
            xlabelname,
            figure_options["x_axis_type"],
            stacked,
            normed,
            **kwargs
        )

    if kind == "pie":

        p = pieplot(
            source, data_cols, colormap, hovertool, figure_options, **kwargs
        )

    # Set xticks:
    if not xticks is None:
        p.xaxis[0].ticker = list(xticks)
    elif xaxis_type == "numerical" and kind not in ["hist", "scatter"]:
        p.xaxis.ticker = x
    if not yticks is None:
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

    # Display plot if wanted
    if show_figure:
        show(p)

    # Return as (embeddable) HTML if wanted:
    if return_html:
        return embedded_html(p)

    # Return plot:
    return p


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
    **kwargs
):
    """Adds lineplot to figure p for each data_col."""

    if "marker" in kwargs:
        marker = kwargs["marker"]
        del kwargs["marker"]
    else:
        marker = "circle"

    # Add line (and optional scatter glyphs) to figure:
    for name, color in zip(data_cols, colormap):
        glyph = p.line(
            x="x", y=name, legend=" " + name, source=source, color=color, **kwargs
        )

        if plot_data_points:
            p.scatter(
                x="x",
                y=name,
                legend=" " + name,
                source=source,
                color=color,
                marker=marker,
                size=plot_data_points_size,
            )

        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if x_axis_type == "datetime":
                my_hover.tooltips = [(xlabelname, "@x{%F}"), (name, "@{%s}" % name)]
                my_hover.formatters = {"x": "datetime"}
            else:
                my_hover.tooltips = [(xlabelname, "@x"), (name, "@{%s}" % name)]
            p.add_tools(my_hover)

    return p


def pointplot(
    p, source, data_cols, colormap, hovertool, xlabelname, x_axis_type, **kwargs
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
            x="x",
            y=name,
            legend=" " + name,
            source=source,
            color=color,
            marker=marker,
            **kwargs
        )
        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if x_axis_type == "datetime":
                my_hover.tooltips = [(xlabelname, "@x{%F}"), (name, "@{%s}" % name)]
                my_hover.formatters = {"x": "datetime"}
            else:
                my_hover.tooltips = [(xlabelname, "@x"), (name, "@{%s}" % name)]
            p.add_tools(my_hover)

    return p


def scatterplot(
    p,
    x,
    y,
    category,
    category_values,
    colormap,
    hovertool,
    x_axis_type,
    xlabelname,
    ylabelname,
    **kwargs
):
    """Adds a scatterplot to figure p for each data_col."""

    # Set standard size and linecolor of markers:
    if "size" not in kwargs:
        kwargs["size"] = 10
    if "line_color" not in kwargs:
        kwargs["line_color"] = "black"

    # Define source:
    source = ColumnDataSource({"x": x, "y": y})

    # Define Colormapper for categorical scatterplot:
    if not category is None:

        category = str(category)
        source.data[category] = category_values

        # Make numerical categorical scatterplot:
        if check_type(category_values) == "numeric":

            kwargs["legend"] = category + " "

            # Define colormapper for numerical scatterplot:
            if colormap == None:
                colormap = Inferno256
            elif isinstance(colormap, str):
                if colormap in all_palettes:
                    colormap = all_palettes[colormap]
                    max_key = max(colormap.keys())
                    colormap = colormap[max_key]
                else:
                    raise ValueError(
                        "Could not find <colormap> with name %s. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): %s"
                        % (colormap, list(all_palettes.keys()))
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
            glyph = p.scatter(x="x", y="y", source=source, **kwargs)

            # Add Hovertool
            if hovertool:
                my_hover = HoverTool(renderers=[glyph])
                if x_axis_type == "datetime":
                    my_hover.tooltips = [(xlabelname, "@x{%F}"), (ylabelname, "@y")]
                    my_hover.formatters = {"x": "datetime"}
                else:
                    my_hover.tooltips = [(xlabelname, "@x"), (ylabelname, "@y")]
                my_hover.tooltips.append((str(category), "@{%s}" % category))
                p.add_tools(my_hover)

        # Make categorical scatterplot:
        elif check_type(category_values) == "object":

            # Define colormapper for categorical scatterplot:
            labels, categories = pd.factorize(category_values)
            colormap = get_colormap(colormap, len(categories))

            # Draw each category as separate glyph:
            x, y = source.data["x"], source.data["y"]
            for cat, color in zip(categories, colormap):
                x_cat = x[category_values == cat]
                y_cat = y[category_values == cat]
                cat_cat = category_values[category_values == cat]
                source = ColumnDataSource({"x": x_cat, "y": y_cat, "category": cat_cat})

                # Draw glyph:
                glyph = p.scatter(
                    x="x",
                    y="y",
                    legend=str(cat) + " ",
                    source=source,
                    color=color,
                    **kwargs
                )

                # Add Hovertool
                if hovertool:
                    my_hover = HoverTool(renderers=[glyph])
                    if x_axis_type == "datetime":
                        my_hover.tooltips = [(xlabelname, "@x{%F}"), (ylabelname, "@y")]
                        my_hover.formatters = {"x": "datetime"}
                    else:
                        my_hover.tooltips = [(xlabelname, "@x"), (ylabelname, "@y")]
                    my_hover.tooltips.append((str(category), "@category"))
                    p.add_tools(my_hover)

            if len(categories) > 5:
                warnings.warn(
                    "There are more than 5 categories in the scatterplot. The legend might be crowded, to hide the axis you can pass 'legend=False' as an optional argument."
                )

        else:
            raise ValueError(
                "<category> is not supported with datetime objects. Consider casting the datetime objects to strings, which can be used as <category> values."
            )

    # Draw non categorical plot:
    else:
        # Draw glyph:
        glyph = p.scatter(x="x", y="y", source=source, **kwargs)

        # Add Hovertool:
        if hovertool:
            my_hover = HoverTool(renderers=[glyph])
            if x_axis_type == "datetime":
                my_hover.tooltips = [(xlabelname, "@x{%F}"), (ylabelname, "@y")]
                my_hover.formatters = {"x": "datetime"}
            else:
                my_hover.tooltips = [(xlabelname, "@x"), (ylabelname, "@y")]
            p.add_tools(my_hover)

    return p


def histogram(
    p,
    data_cols,
    colormap,
    aggregates,
    bins,
    averages,
    hovertool,
    normed,
    cumulative,
    show_average,
    histogram_type,
    logy,
    **kwargs
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
            legend=name,
            **kwargs
        )

        if hovertool:
            my_hover = HoverTool(mode="vline", renderers=[g1])
            my_hover.tooltips = (
                """<h3> %s: </h3> <h4>bin=@bins</h4> <h4>value=@top </h4>""" % (name)
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
                    legend="<%s> = %f" % (name, average),
                )

    p.xaxis.ticker = bins

    return p


def areaplot(
    p,
    source,
    data_cols,
    colormap,
    hovertool,
    xlabelname,
    x_axis_type,
    stacked,
    normed,
    **kwargs
):
    """Adds areaplot to figure p for each data_col."""

    # Transform columns to be able to plot areas as patched:
    if not stacked:
        line_source = deepcopy(source)
        for key in list(source.keys()):
            if key == "x":
                source[key] = [source[key][0]] + list(source[key]) + [source[key][-1]]
            else:
                source[key] = np.array([0] + list(source[key]) + [0])
    else:
        if normed is not False:
            data = []
            for col in data_cols:
                data.append(source[col])
            data = np.array(data)
            norm = np.sum(data, axis=0)
            for col in data_cols:
                source[col] = np.array(source[col]) / norm * normed

        line_source = {"x": source["x"]}
        baseline = np.zeros(len(source["x"]))
        source["x"] = list(source["x"]) + list(source["x"])[::-1]
        for j, col in enumerate(data_cols):

            # Stack lines:
            line_source[col + "_plot"] = baseline + np.array(source[col])
            line_source[col] = np.array(source[col])

            # Stack patches:
            source[col] = baseline + np.array(source[col])
            new_baseline = source[col]
            source[col] = list(source[col]) + list(baseline)[::-1]
            baseline = new_baseline

    if "alpha" not in kwargs:
        kwargs["alpha"] = 0.5

    # Add area patches to figure:
    for j, name, color in list(zip(range(len(data_cols)), data_cols, colormap))[::-1]:
        p.patch(x="x", y=name, legend=" " + name, source=source, color=color, **kwargs)

        # Add hovertool:
        if hovertool and int(len(data_cols) / 2) == j + 1:

            # Add single line for displaying hovertool:
            if stacked:
                y = name + "_plot"
            else:
                y = name
            glyph = p.line(
                x="x", y=y, legend=" " + name, source=line_source, color=color, alpha=0
            )

            # Define hovertool and add to line:
            my_hover = HoverTool(mode="vline", renderers=[glyph])
            if x_axis_type == "datetime":
                my_hover.tooltips = [(xlabelname, "@x{%F}")] + [
                    (name, "@{%s}" % name) for name in data_cols[::-1]
                ]
                my_hover.formatters = {"x": "datetime"}
            else:
                my_hover.tooltips = [(xlabelname, "@x"), (name, "@{%s}" % name)]
            p.add_tools(my_hover)

    return p


def pieplot(
    source, data_cols, colormap, hovertool, figure_options, **kwargs
):

    """Creates a Pieplot from the provided data."""

    # Determine Colormap for Pieplot:
    colormap = get_colormap(colormap, len(source["x"]))
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
        source["inner_radius"] = [inner_radius] * len(source["x"])
        source["outer_radius"] = [outer_radius] * len(source["x"])
        if i == 0:
            legend = "x"
        else:
            legend = False

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
            legend=legend,
            source=source,
            **kwargs
        )

        # Add annotation:
        if len(data_cols) > 1:
            text_source = {
                "x": [-1.3 - 0.05 * max_col_stringlength],
                "y": [0.5 - 0.3 * i],
                "text": [col],
            }
            ann = p.text(
                x="x", y="y", text="text", text_font_style="bold", source=text_source
            )

            p.line(
                x=[-1.3 - 0.04*(max_col_stringlength - len(col)), 0],
                y=[0.5 - 0.3 * i, -(inner_radius + outer_radius) / 2],
                line_color="black"
            )

        # Define hovertool and add to Pieplot:
        if hovertool:
            my_hover = HoverTool(renderers=[glyph])
            my_hover.tooltips = [
                (figure_options["x_axis_label"], "@x"),
                (col, "@{%s}" % col),
            ]
            p.add_tools(my_hover)

    return p


##############################################################################
###########Class to add Bokeh plotting methods to Pandas DataFrame
##############################################################################


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
        return plot(self._data, *args, **kwargs)

    __call__.__doc__ = plot.__doc__

    def line(self, *args, **kwargs):
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

            >>> lines = df.plot.line(x='pig', y='horse')
        """
        return self(kind="line", *args, **kwargs)

