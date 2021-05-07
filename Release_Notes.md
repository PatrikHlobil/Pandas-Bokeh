# Release Notes

## 0.0.1

In this early version, the following plot types are supported:

* line
* point
* scatter
* bar
* histogram

In the near future many more will be implemented as horizontal barplot, boxplots,pie-charts, etc.

**Pandas-Bokeh** is a high-level API for *Bokeh*. Nevertheless there are many options for customizing the plots, for example:

* **figsize**: Choose width & height of the plot
* **title**: Sets title of the plot
* **xlim**/**ylim**: Set visibler range of plot for x- and y-axis (also works for *datetime x-axis*)
* **xlabel**/**ylabel**: Set x- and y-labels
* **logx**/**logy**: Set log-scale on x-/y-axis
* **xticks**/**yticks**: Explicitly set the ticks on the axes
* **colormap**: Defines the colors to plot. Can be either a list of colors or the name of a [Bokeh color palette](https://bokeh.pydata.org/en/latest/docs/reference/palettes.html)
* **hovertool**: If True a Hovertool is active, else if False no Hovertool is drawn.

Plots like scatterplot or histogram also have many more additional customization options.

## 0.0.2:

**Changes:**

* Fixed Error when importing **Pandas-Bokeh** in Python 2.7 
* Small refactoring and *Black* code formatting

## 0.1

**Changes:**

### General
* WebGL now as plotting backend as default 
* Code Refactoring & many bugfixes
* Added panning/zooming keyword options
* Toolbar now visible per default
* Kwargs names are checked in columns of DataFrame/Series and kept if there is a match, such that additional keyword arguments can be used to specify for example line_width or alpha value of plots
* Improved Functionalities (row, column) for **Pandas-Bokeh** Layouts
* Added <hovertool_string> for providing an [HTML string to the hovertool](https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#custom-tooltip)
* Many additional customization arguments

#### DataFrames
* Additional plot types:
    * areaplots (with **stacked** and **normed** kwargs)
    * horizontal & stacked barplots 
    * piecharts
    * mapplot
* Added accessors similar to the pandas.DataFrame.plot API:
  * ```df.plot_bokeh(kind="line", ...)``` → ```df.plot_bokeh.line(...)```
  * ```df.plot_bokeh(kind="bar", ...)``` → ```df.plot_bokeh.bar(...)```
  * ```df.plot_bokeh(kind="hist", ...)``` → ```df.plot_bokeh.hist(...)```
  * ...
* Smarter x-axis formatting for barplots when using datetimes
* Histogram <bins> parameter also accepts integers (to specify number of bins)
* Added support for categorical x-axis for all plot types (line, scatter, area, ...)
* Smarter autodetection of x- and y-labels

#### GeoDataFrames
* Added <tile_attribution> & <tile_alpha> parameter for background tiles of geoplots
* Support for xlim & ylim in WGS84 (Latitude/Longitude) for geoplots
* Greatly Improved performance for Polygon Geoplots 


## 0.1.1

* Refactoring of mapplot API (calls GeoPandas API of Pandas-Bokeh), such that all options of GeoPandas.GeoDataFrame.plot_bokeh are available.
* Allow passing a Pandas_Bokeh figure to overlay geoplots (not fully supported for category/dropdown/slider yet)
* Bug Fix for new **Pandas 0.24** release
* Implementation of first tests 

## 0.2

* **PySpark** support
* **Zeppelin Notebooks** support
* Added "disable_scientific_axes" option for Plots
* Bugfixes
* Implementation of **number_format** keyword for line, scatterplots
* Official support also for Python 3.4 & 3.5 

## 0.3

* Official Pandas backend switch support for pandas >= 0.25
* Add **stepplot**
* Add support for colormap ticker formatting in Geoplots
* Support for multipolygons & holes in Geoplots
* Bugfixes
* conda support

## 0.4

* Rangetool support
* Autoscaling support using the **sizing_mode** keyword
* Bugfixes 

## 0.4.1

* speedup when plotting GeoDataFrames

## 0.4.2

* Bugfixes

## 0.4.3

* Bugfixes (#55-Multipolygon plotting error)
* Improvements with sizing & zooming (#61)

## 0.5

* Implementation of **geometry_column**-parameter for geoplots (#14 Plotting LineString)
* Fix of deprecation warnings for Bokeh >= 2.0 and future minimum requirement Bokeh>=2.0 (#51-BokehDeprecationWarnings with Bokeh v1.4.0, #59-Bokeh 2.0 is imminent)
* Fix of Problem with Datetime Hovertool columns with Bokeh>=2.0 (#60-Hovertool datetime shows as percentage.)
* Fix broken Dropdown and Slider for Geoplots (#68 Not compatible with Bokeh 2.x)
* Added fontsize settings for Labels, Title and Ticks

## 0.5.1

* bugfixes

## 0.5.2

* bugfixes

## 0.5.3

* keep aspect ratio for map-plots
* add support for Bokeh 2.3

## 0.5.4

* fix problem with Pandas Extension-Datatypes (#94)
* fix problem when passing string-values to `bins` (#96)

## 0.5.5

* Display adaptive xticks per default
