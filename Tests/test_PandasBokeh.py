import json
import os

import numpy as np
import pandas as pd
import pytest

import pandas_bokeh

DIRECTORY = os.path.dirname(__file__)
TEST_SETS_DIRECTORY = os.path.join(os.path.dirname(DIRECTORY), "docs", "Testdata")

os.makedirs(os.path.join(DIRECTORY, "Plots"), exist_ok=True)

# Set pandas plotting backend:
pd.set_option("plotting.backend", "pandas_bokeh")

##############################################################################
#################################FIXTURES#####################################
##############################################################################


@pytest.fixture(scope="function")
def df_stock():

    np.random.seed(42)
    df_stock = pd.DataFrame(
        {"Google": np.random.randn(1000) + 0.2, "Apple": np.random.randn(1000) + 0.17},
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df_stock.index.name = "Date"
    df_stock = df_stock.cumsum()
    df_stock = df_stock + 50

    return df_stock


@pytest.fixture(scope="function")
def df_iris():

    # Load Iris Dataset:
    df_iris = pd.read_csv(os.path.join(TEST_SETS_DIRECTORY, "iris", "iris.csv"))

    return df_iris


@pytest.fixture(scope="function")
def df_fruits():

    data = {
        "fruits": ["Apples", "Pears", "Nectarines", "Plums", "Grapes", "Strawberries"],
        "2015": [2, 1, 4, 3, 2, 4],
        "2016": [5, 3, 3, 2, 4, 6],
        "2017": [3, 2, 4, 4, 5, 3],
    }

    df_fruits = pd.DataFrame(data).set_index("fruits")

    return df_fruits


@pytest.fixture(scope="function")
def df_hist():

    np.random.seed(42)

    df_hist = pd.DataFrame(
        {
            "a": np.random.randn(1000) + 1,
            "b": np.random.randn(1000),
            "c": np.random.randn(1000) - 1,
        },
        columns=["a", "b", "c"],
    )

    return df_hist


@pytest.fixture(scope="function")
def df_energy():

    df_energy = pd.read_csv(
        os.path.join(TEST_SETS_DIRECTORY, "energy", "energy.csv"), parse_dates=["Year"]
    )

    return df_energy


@pytest.fixture(scope="function")
def df_election():

    df_election = pd.read_csv(
        os.path.join(TEST_SETS_DIRECTORY, "Bundestagswahl", "Bundestagswahl.csv")
    )

    return df_election


@pytest.fixture(scope="function")
def df_mapplot():

    df_mapplot = pd.read_csv(
        os.path.join(TEST_SETS_DIRECTORY, "populated places", "populated_places.csv")
    )
    df_mapplot["size"] = df_mapplot["pop_max"] / 1000000

    return df_mapplot


##############################################################################
##################################TESTS#######################################
##############################################################################


def test_basic_lineplot(df_stock):
    """Test for basic lineplot"""

    # Create basic lineplot:
    p_basic_lineplot = df_stock.plot_bokeh(kind="line", show_figure=False)
    p_basic_lineplot_accessor = df_stock.plot_bokeh.line(show_figure=False)

    p_basic_lineplot_pandas_backend = df_stock.plot(
        kind="line",
        fontsize_title=30,
        fontsize_label=25,
        fontsize_ticks=15,
        fontsize_legend=40,
        show_figure=False,
    )
    p_basic_lineplot_accessor_pandas_backend = df_stock.plot.line(
        fontsize_title=30,
        fontsize_label=25,
        fontsize_ticks=15,
        fontsize_legend=40,
        show_figure=False,
    )

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_basic_lineplot,
            p_basic_lineplot_accessor,
            p_basic_lineplot_pandas_backend,
            p_basic_lineplot_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Basic_lineplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_basic_lineplot_rangetool(df_stock):
    """Test for basic lineplot above with a rangetool extension"""

    p_basic_lineplot_accessor_pandas_backend = df_stock.plot.line(
        show_figure=False, rangetool=True
    )

    # Output plot as HTML:
    pandas_bokeh.output_file(
        os.path.join(DIRECTORY, "Plots", "Basic_lineplot_rangetool.html")
    )
    pandas_bokeh.save(p_basic_lineplot_accessor_pandas_backend)

    assert True


def test_complex_lineplot(df_stock):
    """Test for complexd lineplot"""

    # Create complex lineplot:
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
    p_complex_lineplot = df_stock.plot_bokeh(kind="line", **arguments)
    p_complex_lineplot_accessor = df_stock.plot_bokeh.line(**arguments)

    p_complex_lineplot_pandas_backend = df_stock.plot(kind="line", **arguments)
    p_complex_lineplot_accessor_pandas_backend = df_stock.plot.line(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_complex_lineplot,
            p_complex_lineplot_accessor,
            p_complex_lineplot_pandas_backend,
            p_complex_lineplot_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Complex_lineplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_lineplot_with_points(df_stock):
    "Test for lineplot with data points:"

    # Create complex lineplot:
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
    p_lineplot_with_points = df_stock.plot_bokeh(kind="line", **arguments)
    p_lineplot_with_points_accessor = df_stock.plot_bokeh.line(**arguments)

    p_lineplot_with_points_pandas_backend = df_stock.plot(kind="line", **arguments)
    p_lineplot_with_points_accessor_pandas_backend = df_stock.plot.line(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_lineplot_with_points,
            p_lineplot_with_points_accessor,
            p_lineplot_with_points_pandas_backend,
            p_lineplot_with_points_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Lineplot_with_points.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_basic_stepplot(df_stock):
    """Test for basic stepplot"""

    p_basic_stepplot = df_stock.plot_bokeh(kind="step", show_figure=False)
    p_basic_stepplot_accessor = df_stock.plot_bokeh.step(show_figure=False)

    p_basic_stepplot_pandas_backend = df_stock.plot(kind="step", show_figure=False)
    p_basic_stepplot_accessor_pandas_backend = df_stock.plot.step(show_figure=False)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_basic_stepplot,
            p_basic_stepplot_accessor,
            p_basic_stepplot_pandas_backend,
            p_basic_stepplot_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Basic_stepplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_pointplot():
    "Test for pointplot"

    x = np.arange(-3, 3, 0.1)
    y2 = x ** 2
    y3 = x ** 3
    df = pd.DataFrame({"x": x, "Parabula": y2, "Cube": y3})

    arguments = dict(
        x="x",
        xticks=range(-3, 4),
        size=5,
        colormap=["#009933", "#ff3399"],
        title="Pointplot (Parabula vs. Cube)",
        marker="x",
        show_figure=False,
    )

    p_pointplot = df.plot_bokeh(kind="point", **arguments)
    p_pointplot_accessor = df.plot_bokeh.point(**arguments)

    p_pointplot_pandas_backend = df.plot(kind="point", **arguments)
    p_pointplot_accessor_pandas_backend = df.plot.point(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_pointplot,
            p_pointplot_accessor,
            p_pointplot_pandas_backend,
            p_pointplot_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Pointplot.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_scatterplot(df_iris):
    "Test for scatterplot"

    # Create Bokeh-Table with DataFrame:
    from bokeh.models import ColumnDataSource
    from bokeh.models.widgets import DataTable, TableColumn

    data_table = DataTable(
        columns=[TableColumn(field=Ci, title=Ci) for Ci in df_iris.columns],
        source=ColumnDataSource(df_iris.head(10)),
    )

    data_table_accessor = DataTable(
        columns=[TableColumn(field=Ci, title=Ci) for Ci in df_iris.columns],
        source=ColumnDataSource(df_iris.head(10)),
    )

    # Create Scatterplot:
    arguments = dict(
        x="petal length (cm)",
        y="sepal width (cm)",
        category="species",
        title="Iris DataSet Visualization",
        show_figure=False,
    )

    p_scatter = df_iris.plot_bokeh(kind="scatter", **arguments)
    p_scatter_accessor = df_iris.plot_bokeh.scatter(**arguments)

    p_scatter_pandas_backend = df_iris.plot(kind="scatter", **arguments)
    p_scatter_accessor_pandas_backend = df_iris.plot.scatter(**arguments)

    # Combine Div and Scatterplot via grid layout:
    output = pandas_bokeh.plot_grid(
        [
            [data_table, p_scatter],
            [
                data_table_accessor,
                p_scatter_accessor,
                p_scatter_pandas_backend,
                p_scatter_accessor_pandas_backend,
            ],
        ],
        show_plot=False,
        return_html=True,
    )

    with open(os.path.join(DIRECTORY, "Plots", "Scatterplot.html"), "w") as f:
        f.write(output)

    assert True


def test_scatterplot_2(df_iris):
    "Test 2 for scatterplot"

    # Change one value to clearly see the effect of the size keyword
    df_iris.loc[13, "sepal length (cm)"] = 15

    # Make scatterplot:
    # Create Scatterplot:
    arguments = dict(
        x="petal length (cm)",
        y="sepal width (cm)",
        category="species",
        title="Iris DataSet Visualization",
        size="sepal length (cm)",
        show_figure=False,
    )

    p_scatter = df_iris.plot_bokeh(kind="scatter", **arguments)
    p_scatter_accessor = df_iris.plot_bokeh.scatter(**arguments)

    p_scatter_pandas_backend = df_iris.plot(kind="scatter", **arguments)
    p_scatter_accessor_pandas_backend = df_iris.plot.scatter(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [
            p_scatter,
            p_scatter_accessor,
            p_scatter_pandas_backend,
            p_scatter_accessor_pandas_backend,
        ]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Scatterplot_2.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_barplot_basic(df_fruits):
    "Basic Test for Barplot"

    # Create Scatterplot:
    arguments = dict(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        show_figure=False,
    )

    p_bar = df_fruits.plot_bokeh(kind="bar", **arguments)
    p_bar_accessor = df_fruits.plot_bokeh.bar(**arguments)

    p_bar_pandas_backend = df_fruits.plot(kind="bar", **arguments)
    p_bar_accessor_pandas_backend = df_fruits.plot.bar(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [p_bar, p_bar_accessor, p_bar_pandas_backend, p_bar_accessor_pandas_backend]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Barplot_basic.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_barplot_stacked(df_fruits):
    "Test for stacked Barplot"

    # Create Scatterplot:
    arguments = dict(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        stacked=True,
        alpha=0.6,
        show_figure=False,
    )

    p_bar = df_fruits.plot_bokeh(kind="bar", **arguments)
    p_bar_accessor = df_fruits.plot_bokeh.bar(**arguments)

    p_bar_pandas_backend = df_fruits.plot(kind="bar", **arguments)
    p_bar_accessor_pandas_backend = df_fruits.plot.bar(**arguments)

    # Output plot as HTML:
    output = pandas_bokeh.row(
        [p_bar, p_bar_accessor, p_bar_pandas_backend, p_bar_accessor_pandas_backend]
    )
    with open(os.path.join(DIRECTORY, "Plots", "Barplot_stacked.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True


def test_barplot_layout(df_fruits):
    "Test for Barplot layout"

    p_bar = df_fruits.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        show_figure=False,
    )

    p_stacked_bar = df_fruits.plot_bokeh.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        stacked=True,
        alpha=0.6,
        show_figure=False,
    )

    p_bar_pandas_backend = df_fruits.plot.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        show_figure=False,
    )

    p_stacked_bar_pandas_backend = df_fruits.plot.bar(
        ylabel="Price per Unit [€]",
        title="Fruit prices per Year",
        stacked=True,
        alpha=0.6,
        show_figure=False,
    )

    # Reset index, such that "fruits" is now a column of the DataFrame:
    df_fruits.reset_index(inplace=True)

    p_hbar = df_fruits.plot_bokeh(
        kind="barh",
        x="fruits",
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    p_stacked_hbar = df_fruits.plot_bokeh.barh(
        x="fruits",
        stacked=True,
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    p_hbar_pandas_backend = df_fruits.plot(
        kind="barh",
        x="fruits",
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    p_stacked_hbar_pandas_backend = df_fruits.plot.barh(
        x="fruits",
        stacked=True,
        xlabel="Price per Unit [€]",
        title="Fruit prices per Year",
        alpha=0.6,
        legend="bottom_right",
        show_figure=False,
    )

    # Plot all barplot examples in a grid:
    output = pandas_bokeh.plot_grid(
        [
            [p_bar, p_stacked_bar, p_bar_pandas_backend, p_stacked_bar_pandas_backend],
            [
                p_hbar,
                p_stacked_hbar,
                p_hbar_pandas_backend,
                p_stacked_hbar_pandas_backend,
            ],
        ],
        plot_width=450,
        show_plot=False,
        return_html=True,
    )

    # Output plot as HTML:
    with open(os.path.join(DIRECTORY, "Plots", "Barplot_layout.html"), "w") as f:
        f.write(output)

    assert True


def test_histogram(df_hist):
    "Test for histograms"

    # Top-on-Top Histogram (Default):
    p_tt = df_hist.plot_bokeh.hist(
        bins=np.linspace(-5, 5, 41),
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Top-on-Top)",
        line_color="black",
        show_figure=False,
    )

    # Side-by-Side Histogram (multiple bars share bin side-by-side) also accessible via
    # kind="hist":
    p_ss = df_hist.plot_bokeh(
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
    p_stack = df_hist.plot_bokeh.hist(
        bins=np.linspace(-5, 5, 41),
        histogram_type="stacked",
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Stacked)",
        line_color="black",
        show_figure=False,
    )

    # Top-on-Top Histogram (Default):
    p_tt_pandas_backend = df_hist.plot.hist(
        bins=np.linspace(-5, 5, 41),
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Top-on-Top)",
        line_color="black",
        show_figure=False,
    )

    # Side-by-Side Histogram (multiple bars share bin side-by-side) also accessible via
    # kind="hist":
    p_ss_pandas_backend = df_hist.plot(
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
    p_stack_pandas_backend = df_hist.plot.hist(
        bins=np.linspace(-5, 5, 41),
        histogram_type="stacked",
        vertical_xlabel=True,
        hovertool=False,
        title="Normal distributions (Stacked)",
        line_color="black",
        show_figure=False,
    )

    layout = pandas_bokeh.column(
        [
            pandas_bokeh.row(p_tt, p_tt_pandas_backend),
            pandas_bokeh.row(p_ss, p_ss_pandas_backend),
            pandas_bokeh.row(p_stack, p_stack_pandas_backend),
        ]
    )
    pandas_bokeh.output_file(os.path.join(DIRECTORY, "Plots", "Histogram.html"))
    pandas_bokeh.save(layout)


def test_histogram_average_diplay(df_hist):
    "Test average & cumulative function of histogram"

    p_hist = df_hist.plot_bokeh.hist(
        y=["a", "b"],
        bins=np.arange(-4, 6.5, 0.5),
        normed=100,
        vertical_xlabel=True,
        ylabel="Share[%]",
        title="Normal distributions (normed)",
        show_average=True,
        xlim=(-4, 6),
        ylim=(0, 30),
        show_figure=False,
    )

    p_hist_cum = df_hist.plot_bokeh.hist(
        y=["a", "b"],
        bins=np.arange(-4, 6.5, 0.5),
        normed=100,
        cumulative=True,
        vertical_xlabel=True,
        ylabel="Share[%]",
        title="Normal distributions (normed & cumulative)",
        show_figure=False,
    )

    p_hist_cum_pandas_backend = df_hist.plot.hist(
        by=["a", "b"],
        bins=np.arange(-4, 6.5, 0.5),
        normed=100,
        cumulative=True,
        vertical_xlabel=True,
        ylabel="Share[%]",
        title="Normal distributions (normed & cumulative)",
        show_figure=False,
    )

    p_average = pandas_bokeh.plot_grid(
        [[p_hist, p_hist_cum, p_hist_cum_pandas_backend]],
        plot_width=450,
        plot_height=300,
        show_plot=False,
    )

    pandas_bokeh.output_file(
        os.path.join(DIRECTORY, "Plots", "Histogram_average_and_cumulative.html")
    )
    pandas_bokeh.save(p_average)


def test_area_plots(df_energy):
    "Test area plots"

    p_area = df_energy.plot_bokeh.area(
        x="Year",
        stacked=True,
        legend="top_left",
        colormap=["brown", "orange", "black", "grey", "blue", "green"],
        title="Worldwide energy consumption split by energy source",
        ylabel="Million tonnes oil equivalent",
        ylim=(0, 16000),
        show_figure=False,
    )

    p_area_normed = df_energy.plot_bokeh(
        kind="area",
        x="Year",
        stacked=True,
        normed=100,
        legend="bottom_left",
        colormap=["brown", "orange", "black", "grey", "blue", "green"],
        title="Worldwide energy consumption split by energy source",
        ylabel="Million tonnes oil equivalent",
        show_figure=False,
    )

    p_area_pandas_backend = df_energy.plot.area(
        x="Year",
        stacked=True,
        legend="top_left",
        colormap=["brown", "orange", "black", "grey", "blue", "green"],
        title="Worldwide energy consumption split by energy source",
        ylabel="Million tonnes oil equivalent",
        ylim=(0, 16000),
        show_figure=False,
    )

    p_area_normed_pandas_backend = df_energy.plot(
        kind="area",
        x="Year",
        stacked=True,
        normed=100,
        legend="bottom_left",
        colormap=["brown", "orange", "black", "grey", "blue", "green"],
        title="Worldwide energy consumption split by energy source",
        ylabel="Million tonnes oil equivalent",
        show_figure=False,
    )

    layout = pandas_bokeh.plot_grid(
        [
            [p_area, p_area_normed],
            [p_area_pandas_backend, p_area_normed_pandas_backend],
        ],
        plot_width=450,
        plot_height=300,
        show_plot=False,
    )

    pandas_bokeh.output_file(os.path.join(DIRECTORY, "Plots", "Areaplot.html"))
    pandas_bokeh.save(layout)


def test_pieplot(df_election):
    "Test Pieplot"

    p_pie = df_election.plot_bokeh.pie(
        x="Partei",
        y="2017",
        colormap=["blue", "red", "yellow", "green", "purple", "orange", "grey"],
        title="Results of German Bundestag Election 2017",
        show_figure=False,
    )

    p_pie_multiple = df_election.plot_bokeh(
        kind="pie",
        x="Partei",
        colormap=["blue", "red", "yellow", "green", "purple", "orange", "grey"],
        title="Results of German Bundestag Elections [2002-2017]",
        line_color="grey",
        show_figure=False,
    )

    p_pie_pandas_backend = df_election.plot.pie(
        x="Partei",
        y="2017",
        colormap=["blue", "red", "yellow", "green", "purple", "orange", "grey"],
        title="Results of German Bundestag Election 2017",
        show_figure=False,
    )

    p_pie_multiple_pandas_backend = df_election.plot(
        kind="pie",
        x="Partei",
        colormap=["blue", "red", "yellow", "green", "purple", "orange", "grey"],
        title="Results of German Bundestag Elections [2002-2017]",
        line_color="grey",
        show_figure=False,
    )

    layout = pandas_bokeh.plot_grid(
        [
            [p_pie, p_pie_multiple],
            [p_pie_pandas_backend, p_pie_multiple_pandas_backend],
        ],
        plot_width=450,
        plot_height=300,
        show_plot=False,
    )

    pandas_bokeh.output_file(os.path.join(DIRECTORY, "Plots", "Pieplot.html"))
    pandas_bokeh.save(layout)


def test_mapplot(df_mapplot):
    "Mapplot test"

    kwargs = dict(
        x="longitude",
        y="latitude",
        hovertool_string="""<h2> @{name} </h2>

                            <h3> Population: @{pop_max} </h3>""",
        tile_provider="STAMEN_TERRAIN_RETINA",
        size="size",
        figsize=(900, 600),
        title="World cities with more than 1.000.000 inhabitants",
        show_figure=False,
    )

    p_map = df_mapplot.plot_bokeh(kind="map", **kwargs)
    p_map_accessor = df_mapplot.plot_bokeh.map(**kwargs)

    p_map_pandas_backend = df_mapplot.plot(kind="map", **kwargs)
    p_map_accessor_pandas_backend = df_mapplot.plot.map(**kwargs)

    layout = pandas_bokeh.plot_grid(
        [
            [p_map, p_map_accessor],
            [p_map_pandas_backend, p_map_accessor_pandas_backend],
        ],
        plot_width=450,
        plot_height=300,
        show_plot=False,
    )

    pandas_bokeh.output_file(os.path.join(DIRECTORY, "Plots", "Mapplot.html"))
    pandas_bokeh.save(layout)


def test_autosizing(df_fruits):
    """
    Autoscaling test
    """

    kwargs = dict(figsize=(500, 200), sizing_mode="scale_width", show_figure=False)

    p_autoscale = df_fruits.plot_bokeh(kind="bar", **kwargs)
    pandas_bokeh.output_file(os.path.join(DIRECTORY, "Plots", "AutoScale.html"))
    pandas_bokeh.save(p_autoscale)

    assert True
