#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bokeh.plotting import show
from bokeh.layouts import gridplot
import bokeh.plotting
from bokeh.embed import components
from bokeh.resources import CDN


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


def embedded_html(fig, resources="CDN"):
    """Returns an html string that contains all neccessary CSS&JS files, 
    together with the div containing the Bokeh plot. As input, a figure fig
    is expected."""

    html_embedded = ""
    if resources == "CDN":
        # Pack CDN resources:
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
    elif resources == "raw":
        raise NotImplementedError("<resources> = raw has to be implemented by Thomas!")
    elif resources == None:
        pass
    else:
        raise ValueError("<resources> only accept 'CDN', 'raw' or None.")

    # Add plot script and div
    script, div = components(fig)
    html_embedded += "\n\n" + script + "\n\n" + div

    return html_embedded


