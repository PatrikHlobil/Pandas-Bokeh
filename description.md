# Pandas Bokeh

**Pandas Bokeh** provides a [Bokeh](https://bokeh.pydata.org/en/latest/) plotting backend for [Pandas](https://pandas.pydata.org/) and [GeoPandas](http://geopandas.org/), similar to the already existing [Visualization](https://pandas.pydata.org/pandas-docs/stable/visualization.html) feature of Pandas. Importing the library adds a complementary plotting method ***plot_bokeh()*** on **DataFrames** and **Series**. It also has native plotting backend support for Pandas >= 0.25.

For more information and examples have a look at the [Github Repository](https://github.com/PatrikHlobil/Pandas-Bokeh).

---

## Installation


You can install **Pandas Bokeh** from *PyPI* via **pip**:

    pip install pandas-bokeh

or *conda*:

    conda install -c patrikhlobil pandas-bokeh

**Pandas Bokeh** is officially supported on Python 3.5 and above.

---

## Description

With **Pandas Bokeh**, creating stunning, interactive, HTML-based visualization is as easy as calling:
```python
df.plot_bokeh()
```

The following plot types are supported:

* line
* step
* point
* scatter
* bar
* histogram
* area
* pie
* mapplot

<br>

Furthermore, also **GeoPandas** and **Pyspark** have a new plotting backend as can be seen in the provided [examples](https://github.com/PatrikHlobil/Pandas-Bokeh#geoplots).

<br>

**Pandas Bokeh** is a high-level API for **Bokeh** on top of **Pandas** and **GeoPandas** that tries to figure out best, what the user wants to plot. Nevertheless, there are many options for customizing the plots, for example:

* **figsize**: Choose width & height of the plot
* **title**: Sets title of the plot
* **xlim**/**ylim**: Set visible range of plot for x- and y-axis (also works for *datetime x-axis*)
* **xlabel**/**ylabel**: Set x- and y-labels
* **logx**/**logy**: Set log-scale on x-/y-axis
* **xticks**/**yticks**: Explicitly set the ticks on the axes
* **colormap**: Defines the colors to plot. Can be either a list of colors or the name of a [Bokeh color palette](https://bokeh.pydata.org/en/latest/docs/reference/palettes.html)
* **hovertool_string**: For customization of hovertool content

Each plot type like scatterplot or histogram further has many more additional customization options that is described [here](https://github.com/PatrikHlobil/Pandas-Bokeh).
