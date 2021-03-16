#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from bokeh.io import save
from bokeh.layouts import column, layout, row

from .base import embedded_html, output_file, output_notebook, plot_grid, show
from .geoplot import geoplot
from .plot import FramePlotMethods, plot

__version__ = "0.5.4"


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
        "scatter",
        "bar",
        "barh",
        "area",
        "pie",
        "hist",
        "map",
    )

    pd.DataFrame.plot._dataframe_kinds = ("map", "scatter")

    # Define additional plotting APIs (not default in pandas.core.plotting defined)
    def mapplot(self, **kwargs):
        return self(kind="map", **kwargs)

    pd.DataFrame.plot.map = mapplot

    def pointplot(self, **kwargs):
        return self(kind="point", **kwargs)

    pd.DataFrame.plot.point = pointplot

    def stepplot(self, **kwargs):
        return self(kind="step", **kwargs)

    pd.DataFrame.plot.step = stepplot

    for kind in ["map", "point", "step"]:
        getattr(pd.DataFrame.plot, kind).__doc__ = getattr(
            FramePlotMethods, kind
        ).__doc__

    # Define API methods on pandas.plotting:
    pd.plotting.output_notebook = output_notebook
    pd.plotting.output_file = output_file
    pd.plotting.plot_grid = plot_grid
    pd.plotting.show = show
    pd.plotting.embedded_html = embedded_html
    pd.plotting.column = column
    pd.plotting.row = row
    pd.plotting.layout = layout
    pd.plotting.save = save


# Define Bokeh-plot method for GeoPandas and Series:
try:
    import geopandas as gpd

    gpd.GeoDataFrame.plot_bokeh = geoplot
    gpd.GeoSeries.plot_bokeh = geoplot

except ImportError:
    pass


# Define Bokeh-plot method for PySpark DataFrames:
if sys.version_info[1] < 8:  # TODO: pyspark currently does not support Python 3.8!
    try:
        import pyspark

        plot_bokeh = CachedAccessor("plot_bokeh", FramePlotMethods)
        pyspark.sql.dataframe.DataFrame.plot_bokeh = plot_bokeh
    except ImportError:
        pass
