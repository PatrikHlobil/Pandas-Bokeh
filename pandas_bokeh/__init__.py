#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import output_notebook, output_file, plot, show, plot_grid, embedded_html
from .geoplot import geoplot

from bokeh.layouts import column, row, layout

import warnings

__version__ = "0.1"

# Define Bokeh-plot method for Pandas DataFrame and Series:
try:
    import pandas as pd

    pd.DataFrame.plot_bokeh = plot
    pd.Series.plot_bokeh = plot
except Exception as e:
    warnings.warn(
        "Could not define plot method for Pandas DataFrame and Series. Please make sure that Pandas is installed if you wish to use Bokeh as plotting backend for Pandas.",
        Warning,
    )


# Define Bokeh-plot method for GeoPandas and Series:
try:
    import geopandas as gpd

    gpd.GeoDataFrame.plot_bokeh = geoplot
    gpd.GeoSeries.plot_bokeh = geoplot
except:
    pass

