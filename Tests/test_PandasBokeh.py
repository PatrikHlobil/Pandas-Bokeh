import json
import pandas as pd
import numpy as np
import pandas_bokeh
import os

directory = os.path.dirname(__file__)


def test_basic_lineplot():
    """Test for basic lineplot"""

    # Create basic lineplot:
    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df.index.name = "Date"
    df = df.cumsum()
    df = df + 50
    p_basic_lineplot = df.plot_bokeh(kind="line", show_figure=False)
    p_basic_lineplot_accessor = df.plot_bokeh.line(show_figure=False)

    # Output plot as HTML:
    output = pandas_bokeh.row([p_basic_lineplot, p_basic_lineplot_accessor])
    with open(os.path.join(directory, "Plots", "Basic_lineplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_complex_lineplot():
    """Test for complexd lineplot"""

    # Create complex lineplot:
    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df.index.name = "Date"
    df = df.cumsum()
    df = df + 50
    arguments = dict(
        figsize=(600, 450),
        y="Apple",
        title="Apple vs Google",
        xlabel="Date",
        ylabel="Stock price [$]",
        yticks=[0, 100, 200, 300, 400],
        ylim=(0, 400),
        toolbar_location=None,
        colormap=["red", "blue"],
        hovertool_string="""<img
                        src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/170px-Apple_logo_black.svg.png" 
                        height="42" alt="@imgs" width="42"
                        style="float: left; margin: 0px 15px 15px 0px;"
                        border="2"></img> Apple 
                        
                        <h4> Stock Price: </h4> @{Apple}""",
        panning=False,
        zooming=False,
        show_figure=False,
    )
    p_complex_lineplot = df.plot_bokeh(kind="line", **arguments)
    p_complex_lineplot_accessor = df.plot_bokeh.line(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row([p_complex_lineplot, p_complex_lineplot_accessor])
    with open(os.path.join(directory, "Plots", "Complex_lineplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_lineplot_with_points():
    "Test for lineplot with data points:"

    # Create complex lineplot:
    np.random.seed(42)
    df = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df.index.name = "Date"
    df = df.cumsum()
    df = df + 50
    arguments = dict(
        figsize=(600, 450),
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
    p_lineplot_with_points = df.plot_bokeh(kind="line", **arguments)
    p_lineplot_with_points_accessor = df.plot_bokeh.line(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row([p_lineplot_with_points, p_lineplot_with_points_accessor])
    with open(os.path.join(directory, "Plots", "Lineplot_with_points.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True




