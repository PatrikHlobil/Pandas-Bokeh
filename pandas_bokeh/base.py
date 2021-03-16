#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bokeh.plotting
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.resources import CDN

OUTPUT_TYPE = "file"
SUPPRESS_OUTPUT = False


def _set_fontsize(figure, fontsize, where):
    "Set fontsize on x- and y-axis"
    if isinstance(fontsize, int) and fontsize > 0:
        fontsize = f"{fontsize}pt"
    setattr(figure.xaxis, where, fontsize)
    setattr(figure.yaxis, where, fontsize)


def set_fontsizes_of_figure(
    figure,
    fontsize_title,
    fontsize_label,
    fontsize_ticks,
    fontsize_legend,
):
    "Set various fontsizes of figure"

    if fontsize_title:
        if isinstance(fontsize_title, int) and fontsize_title > 0:
            fontsize_title = f"{fontsize_title}pt"
        figure.title.text_font_size = fontsize_title

    if fontsize_label:
        _set_fontsize(
            figure=figure, fontsize=fontsize_label, where="axis_label_text_font_size"
        )

    if fontsize_ticks:
        _set_fontsize(
            figure=figure, fontsize=fontsize_ticks, where="major_label_text_font_size"
        )

    if fontsize_legend:
        if isinstance(fontsize_legend, int) and fontsize_legend > 0:
            fontsize_legend = f"{fontsize_legend}pt"
        figure.legend.label_text_font_size = fontsize_legend


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


def output_notebook(notebook_type="auto", **kwargs):
    """Set the output of Bokeh to the current notebook.

    Parameters:
    ----------------------------------------------------------------
    notebook_type (string, default: "auto) - Either "jupyter", "zeppelin" or "auto"
    resources (Resource, optional) – How and where to load BokehJS from (default: CDN)
    verbose (bool, optional) – whether to display detailed BokehJS banner (default: False)
    hide_banner (bool, optional) – whether to hide the Bokeh banner (default: False)
    load_timeout (int, optional) – Timeout in milliseconds when plots assume load
                                   timed out (default: 5000)

    Returns:
    ----------------------------------------------------------------
    None"""

    if notebook_type == "auto":
        notebook_type = detect_notebook_server()
    elif notebook_type in ("jupyter", "zeppelin"):
        pass
    else:
        raise ValueError('<notebook_type> can only be "jupyter", "zeppelin" or "auto"')

    global OUTPUT_TYPE
    OUTPUT_TYPE = notebook_type

    # Reset Bokeh output:
    bokeh.plotting.reset_output()

    if notebook_type == "jupyter":
        bokeh.plotting.output_notebook(**kwargs)
    else:
        # Preload JS resources:
        print("%html\n\n" + get_bokeh_resources())


def detect_notebook_server():
    "Autodetects if user is in Jupyter or Zeppelin notebook."

    try:
        get_ipython()  # noqa F821
        return "jupyter"
    except NameError:
        return "zeppelin"


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
    global OUTPUT_TYPE
    OUTPUT_TYPE = "file"

    bokeh.plotting.reset_output()
    bokeh.plotting.output_file(filename, title=title, mode=mode, root_dir=root_dir)


def show(
    obj, browser=None, new="tab", notebook_handle=False, notebook_url="localhost:8888"
):

    global SUPPRESS_OUTPUT
    if SUPPRESS_OUTPUT:
        return obj

    if OUTPUT_TYPE != "zeppelin":
        bokeh.plotting.show(obj, browser, new, notebook_handle, notebook_url)
    else:
        html_embedded = embedded_html(obj, resources=None)
        print("%html\n\n" + html_embedded)


show.__doc__ = bokeh.plotting.show.__doc__


def embedded_html(fig, resources="CDN"):
    """Returns an html string that contains all neccessary CSS&JS files,
    together with the div containing the Bokeh plot. As input, a figure fig
    is expected."""

    html_embedded = ""
    if resources == "CDN":
        js_css_resources = get_bokeh_resources()
        html_embedded += js_css_resources
    elif resources == "raw":
        raise NotImplementedError("<resources> = raw has to be implemented by Thomas!")
    elif resources is None:
        pass
    else:
        raise ValueError("<resources> only accept 'CDN', 'raw' or None.")

    # Add plot script and div
    script, div = components(fig)
    html_embedded += "\n\n" + div + "\n\n" + script

    return html_embedded


def get_bokeh_resources():
    "Returns string with all JS & CSS resources needed for Bokeh for HTML output"

    # Pack CDN resources:
    js_css_resources = ""
    for css in CDN.css_files:
        js_css_resources += (
            """<link href="%s" rel="stylesheet" type="text/css">\n""" % css
        )

    for js in CDN.js_files:
        js_css_resources += """<script src="%s"></script>\n""" % js

    return js_css_resources
