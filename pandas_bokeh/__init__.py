#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import output_notebook, output_file, plot_grid, show, embedded_html
from .plot import plot, FramePlotMethods
from .geoplot import geoplot

from bokeh.layouts import column, row, layout
from bokeh.io import save

import warnings

__version__ = "0.3"


# Register plot_bokeh accessor for Pandas DataFrames and Series:
import pandas as pd
from pandas.core.accessor import CachedAccessor

plot_bokeh = CachedAccessor("plot_bokeh", FramePlotMethods)
pd.DataFrame.plot_bokeh = plot_bokeh
pd.Series.plot_bokeh = plot

# Add pandas_bokeh as plotting backend option (available for pandas >= 0.25)
if pd.__version__ >= "0.25":
    pd.DataFrame.plot._all_kinds = (
        "line",
        "point",
        "step",
        "bar",
        "barh",
        "area",
        "pie",
        "hist",
        "map",
    )

    # Define additional plotting APIs (not default in pandas.core.plotting defined)
    def mapplot(self, x=None, y=None, **kwargs):
        return self(kind="map", x=x, y=y, **kwargs)
    pd.DataFrame.plot.map = mapplot

    def pointplot(self, x=None, y=None, **kwargs):
        return self(kind="point", x=x, y=y, **kwargs)
    pd.DataFrame.plot.point = pointplot

    def stepplot(self, x=None, y=None, **kwargs):
        return self(kind="step", x=x, y=y, **kwargs)
    pd.DataFrame.plot.step = stepplot

    for kind in ["map", "point", "step"]:
        getattr(pd.DataFrame.plot, kind).__doc__ = getattr(FramePlotMethods, kind).__doc__


# Define Bokeh-plot method for GeoPandas and Series:
try:
    import geopandas as gpd

    gpd.GeoDataFrame.plot_bokeh = geoplot
    gpd.GeoSeries.plot_bokeh = geoplot

except ModuleNotFoundError:
    pass


# Define Bokeh-plot method for PySpark DataFrames:
try:
    import pyspark

    plot_bokeh = CachedAccessor("plot_bokeh", FramePlotMethods)
    pyspark.sql.dataframe.DataFrame.plot_bokeh = plot_bokeh
except ModuleNotFoundError:
    pass
