import setuptools

long_description = """# Pandas Bokeh

**Pandas Bokeh** provides a [Bokeh](https://bokeh.pydata.org/en/latest/) plotting backend for [Pandas](https://pandas.pydata.org/) and [GeoPandas](http://geopandas.org/), similar to the already existing [Visualization](https://pandas.pydata.org/pandas-docs/stable/visualization.html) feature of Pandas. Importing the library adds a complementary plotting method ***plot_bokeh()*** on **DataFrames** and **Series** (and also on **GeoDataFrames**).

For more information and examples have a look at the [Github Repository](https://github.com/PatrikHlobil/Pandas-Bokeh).

---

## Installation


You can install **Pandas Bokeh** from [PyPI](TODO) via *pip*:

    pip install pandas-bokeh

**Pandas Bokeh** is supported on Python 2.7, as well as Python 3.6 and above.

---

## Description

With **Pandas Bokeh**, creating stunning, interactive, HTML-based visualization is as easy as calling:
```python
df.plot_bokeh()
```

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

"""

setuptools.setup(
    name="pandas-bokeh",
    version="0.0.2",
    author="Patrik Hlobil",
    author_email="patrik.hlobil@googlemail.com",
    description="Bokeh plotting backend for Pandas.DataFrames",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PatrikHlobil/Pandas-Bokeh",
    packages=setuptools.find_packages(),
    install_requires=["bokeh", "pandas"],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
)
