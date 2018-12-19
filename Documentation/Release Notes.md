# Release Notes

## 0.0.1

In this early version, the following plot types are supported:

* line
* point
* scatter
* bar
* histogram

In the near future many more will be implemented as horizontal barplot, boxplots,pie-charts, etc.

**Pandas Bokeh** is a high-level API for *Bokeh*. Nevertheless there are many options for customizing the plots, for example:

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

Changes:

* Fixed Error when importing **Pandas Bokeh** in Python 2.7 
* Small refactoring and *Black* code formatting

## 0.1

### Pandas Bokeh
* WebGL now as plotting backend as default 
* Code Refactoring & many bugfixes
* Added panning/zooming keyword options
* Toolbar now visible per default
* Kwargs names are checked in columns of DataFrame/Series and kept if there is a match, such that additional keyword arguments can be used to specify for example line_width or alpha value of plots
* Improved Functionalities (row, column) for **Pandas Bokeh** Layouts
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





