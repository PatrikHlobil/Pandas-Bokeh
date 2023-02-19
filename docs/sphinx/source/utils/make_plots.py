import inspect
import os
import re
from functools import wraps
from pathlib import Path
from shutil import rmtree
from typing import Callable

import numpy as np
import pandas as pd

import pandas_bokeh

BASE_DIR = Path(__file__).parent
TEST_SETS_DIRECTORY = BASE_DIR / "Testdata"


def embeddable(func):
    @wraps(func)
    def embedder(*args, **kwargs):
        return pandas_bokeh.embedded_html(func(*args, **kwargs))

    return embedder


def df_stocks() -> pd.DataFrame:
    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df = df.cumsum()
    df = df + 50

    return df


def df_parabula_cube() -> pd.DataFrame:
    x = np.arange(-3, 3, 0.1)
    y2 = x**2
    y3 = x**3
    df = pd.DataFrame({"x": x, "Parabula": y2, "Cube": y3})

    return df


def df_iris():
    # Load Iris Dataset:
    df_iris = pd.read_csv(os.path.join(TEST_SETS_DIRECTORY, "iris", "iris.csv"))

    return df_iris


def df_fruits():
    data = {
        "fruits": ["Apples", "Pears", "Nectarines", "Plums", "Grapes", "Strawberries"],
        "2015": [2, 1, 4, 3, 2, 4],
        "2016": [5, 3, 3, 2, 4, 6],
        "2017": [3, 2, 4, 4, 5, 3],
    }

    return pd.DataFrame(data).set_index("fruits")


def df_hist():
    return pd.DataFrame(
        {
            "a": np.random.randn(1000) + 1,
            "b": np.random.randn(1000),
            "c": np.random.randn(1000) - 1,
        },
        columns=["a", "b", "c"],
    )


@embeddable
def plot_Startimage():
    # Barplot:
    data = {
        "fruits": ["Apples", "Pears", "Nectarines", "Plums", "Grapes", "Strawberries"],
        "2015": [2, 1, 4, 3, 2, 4],
        "2016": [5, 3, 3, 2, 4, 6],
        "2017": [3, 2, 4, 4, 5, 3],
    }
    df = pd.DataFrame(data).set_index("fruits")
    p_bar = df.plot_bokeh(
        kind="bar",
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        show_figure=False,
    )

    # Lineplot:
    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df = df.cumsum()
    df = df + 50
    p_line = df.plot_bokeh(
        kind="line",
        title="Apple vs Google",
        xlabel="Date",
        ylabel="Stock price [$]",
        yticks=[0, 100, 200, 300, 400],
        ylim=(0, 400),
        colormap=["red", "blue"],
        show_figure=False,
    )

    # Scatterplot:
    df = df_iris()
    p_scatter = df.plot_bokeh(
        kind="scatter",
        x="petal length (cm)",
        y="sepal width (cm)",
        category="species",
        title="Iris DataSet Visualization",
        show_figure=False,
    )

    # Histogram:
    df_hist = pd.DataFrame(
        {
            "a": np.random.randn(1000) + 1,
            "b": np.random.randn(1000),
            "c": np.random.randn(1000) - 1,
        },
        columns=["a", "b", "c"],
    )

    p_hist = df_hist.plot_bokeh(
        kind="hist",
        bins=np.arange(-6, 6.5, 0.5),
        vertical_xlabel=True,
        normed=100,
        hovertool=False,
        title="Normal distributions",
        show_figure=False,
    )

    # Make Dashboard with Grid Layout:
    return pandas_bokeh.plot_grid(
        [[p_line, p_bar], [p_scatter, p_hist]], plot_width=450, show_plot=False
    )


@embeddable
def plot_ApplevsGoogle_1():
    df = df_stocks()
    return df.plot_bokeh(kind="line", show_figure=False)


@embeddable
def plot_ApplevsGoogle_2():
    df = df_stocks()
    return df.plot_bokeh(
        figsize=(800, 450),
        y="Apple",
        title="Apple vs Google",
        xlabel="Date",
        ylabel="Stock price [$]",
        yticks=[0, 100, 200, 300, 400],
        ylim=(0, 400),
        toolbar_location=None,
        colormap=["red", "blue"],
        hovertool_string=r"<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/170px-Apple_logo_black.svg.png' height='42' alt='@imgs' width='42' style='float: left; margin: 0px 15px 15px 0px;' border='2' ></img> Apple \n\n<h4> Stock Price: </h4> @{Apple}",
        panning=False,
        zooming=False,
        show_figure=False,
    )


@embeddable
def plot_ApplevsGoogle_3():
    df = df_stocks()
    return df.plot_bokeh(
        figsize=(800, 450),
        title="Apple vs Google",
        xlabel="Date",
        ylabel="Stock price [$]",
        yticks=[0, 100, 200, 300, 400],
        ylim=(100, 200),
        xlim=("2001-01-01", "2001-02-01"),
        colormap=["red", "blue"],
        plot_data_points=True,
        plot_data_points_size=10,
        marker="asterisk",
        show_figure=False,
    )


@embeddable
def plot_rangetool():
    ts = pd.Series(np.random.randn(1000), index=pd.date_range("1/1/2000", periods=1000))
    df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index, columns=list("ABCD"))
    df = df.cumsum()

    return df.plot_bokeh(rangetool=True, show_figure=False)


@embeddable
def plot_Pointplot():
    df = df_parabula_cube()
    return df.plot_bokeh.point(
        x="x",
        xticks=range(-3, 4),
        size=5,
        colormap=["#009933", "#ff3399"],
        title="Pointplot (Parabula vs. Cube)",
        marker="x",
        show_figure=False,
    )


@embeddable
def plot_Stepplot():
    df = df_parabula_cube()
    return df.plot_bokeh.step(
        x="x",
        xticks=range(-1, 1),
        colormap=["#009933", "#ff3399"],
        title="Pointplot (Parabula vs. Cube)",
        mode="after",
        figsize=(800, 300),
        show_figure=False,
    )


@embeddable
def plot_Scatterplot():
    df = df_iris()
    df = df.sample(frac=1)

    # Create Bokeh-Table with DataFrame:
    from bokeh.models import ColumnDataSource
    from bokeh.models.widgets import DataTable, TableColumn

    data_table = DataTable(
        columns=[TableColumn(field=Ci, title=Ci) for Ci in df.columns],
        source=ColumnDataSource(df.head(10)),
    )

    # Create Scatterplot:
    p_scatter = df.plot_bokeh.scatter(
        x="petal length (cm)",
        y="sepal width (cm)",
        category="species",
        title="Iris DataSet Visualization",
        show_figure=False,
    )

    # Combine Div and Scatterplot via grid layout:
    return pandas_bokeh.plot_grid(
        [[data_table, p_scatter]], plot_width=400, plot_height=350, show_plot=False
    )


@embeddable
def plot_Barplot():
    df = df_fruits()

    return df.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        show_figure=False,
    )


@embeddable
def plot_Barplot2():
    df = df_fruits()

    return df.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        stacked=True,
        alpha=0.6,
        show_figure=False,
    )


@embeddable
def plot_Barplot3():
    df = df_fruits()

    p_bar = df.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        show_figure=False,
    )

    p_stacked_bar = df.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        stacked=True,
        alpha=0.6,
        show_figure=False,
    )

    # Reset index, such that "fruits" is now a column of the DataFrame:
    df.reset_index(inplace=True)

    # Create horizontal bar (via kind keyword):
    p_hbar = df.plot_bokeh(
        kind="barh",
        x="fruits",
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    # Create stacked horizontal bar (via barh accessor):
    p_stacked_hbar = df.plot_bokeh.barh(
        x="fruits",
        stacked=True,
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    return pandas_bokeh.plot_grid(
        [[p_bar, p_stacked_bar], [p_hbar, p_stacked_hbar]],
        plot_width=450,
        show_plot=False,
    )


@embeddable
def plot_Histogram():
    df = df_hist()

    # Top-on-Top Histogram (Default):
    p1 = df.plot_bokeh.hist(
        bins=np.linspace(-5, 5, 41),
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Top-on-Top)",
        line_color="black",
        show_figure=False,
    )

    # Side-by-Side Histogram (multiple bars share bin side-by-side) also accessible via
    # kind="hist":
    p2 = df.plot_bokeh(
        kind="hist",
        bins=np.linspace(-5, 5, 41),
        histogram_type="sidebyside",
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Side-by-Side)",
        line_color="black",
        show_figure=False,
    )

    # Stacked histogram:
    p3 = df.plot_bokeh.hist(
        bins=np.linspace(-5, 5, 41),
        histogram_type="stacked",
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Stacked)",
        line_color="black",
        show_figure=False,
    )

    return pandas_bokeh.plot_grid([[p1], [p2], [p3]], show_plot=False)


def make_and_return_plots() -> dict:
    plots = {}
    for func in _return_plot_functions():
        plotname = func.__name__[5:]
        print(f"Create plot {plotname}")
        plots[plotname] = func()

    return plots


def _return_plot_functions() -> Callable:
    plot_functions = [
        value
        for key, value in globals().items()
        if callable(value) and value.__module__ == __name__ and key.startswith("plot_")
    ]

    return plot_functions


if __name__ == "__main__":
    plots = make_and_return_plots()
    print(list(plots.keys()))
