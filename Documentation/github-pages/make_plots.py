import pandas_bokeh
import pandas as pd
import numpy as np
import inspect
from shutil import rmtree
import os

SUPPRESS_OUTPUT = {"return_html": True, "show_figure": False}

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PLOT_DIR = os.path.join(BASE_DIR, "plots")

rmtree(PLOT_DIR, ignore_errors=True)
os.makedirs(PLOT_DIR, exist_ok=True)


def df_stocks() -> tuple:

    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df = df.cumsum()
    df = df + 50

    return df


def ApplevsGoogle_1():

    df = df_stocks()
    plot = df.plot_bokeh(kind="line", **SUPPRESS_OUTPUT)

    plotname = inspect.stack()[0][3]
    return plotname, plot


def ApplevsGoogle_2() -> tuple:

    df = df_stocks()
    plot = df.plot_bokeh(
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
        **SUPPRESS_OUTPUT
    )

    plotname = inspect.stack()[0][3]

    with open("1.html", "w") as f:
        f.write(plot)
    return plotname, plot


def make_plots() -> dict:

    plots = {}
    for func in [ApplevsGoogle_1, ApplevsGoogle_2]:
        plotname, plot = func()
        plots[plotname] = plot

    return plots


if __name__ == "__main__":

    make_plots()
