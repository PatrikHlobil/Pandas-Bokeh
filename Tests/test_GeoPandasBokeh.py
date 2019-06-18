import json
import pandas as pd
import geopandas as gpd
import numpy as np
import sys

sys.path.append(r"/home/patrik/projects/Pandas-Bokeh")
import pandas_bokeh
import os

directory = os.path.dirname(__file__)
test_sets_directory = os.path.join(
    os.path.dirname(directory), "Documentation", "Testdata"
)
os.makedirs(os.path.join(directory, "Plots"), exist_ok=True)


def test_geolayers_simple():
    "Tests for simple"

    # Read in GeoJSON from URL:
    df_states = gpd.read_file(
        r"https://raw.githubusercontent.com/PatrikHlobil/Pandas-Bokeh/master/Documentation/Testdata/states/states.geojson"
    )

    figure = df_states.plot_bokeh(simplify_shapes=10000, show_figure=False)

    with open(  # +ä
        os.path.join(directory, "Plots", "Geolayers_Simple.html"), "w"
    ) as f:
        f.write(pandas_bokeh.embedded_html(figure))

    assert True


def test_geolayers_slider():
    "Tests for mutiple geolayers"

    # Read in GeoJSON from URL:
    df_states = gpd.read_file(
        os.path.join(test_sets_directory, "states", "states.geojson")
    )
    df_cities = gpd.read_file(
        os.path.join(
            test_sets_directory,
            "populated places",
            "ne_10m_populated_places_simple_bigcities.geojson",
        )
    )
    df_cities["size"] = df_cities.pop_max / 400000

    # Calculate change of population relative to 2010:
    for i in range(8):
        df_states["Delta_Population_201%d" % i] = (
            (df_states["POPESTIMATE201%d" % i] / df_states["POPESTIMATE2010"]) - 1
        ) * 100

    # Specify slider columns:
    slider_columns = ["Delta_Population_201%d" % i for i in range(8)]

    # Specify slider-range (Maps "Delta_Population_2010" -> 2010,
    #                           "Delta_Population_2011" -> 2011, ...):
    slider_range = range(2010, 2018)

    # Make slider plot:

    # Plot shapes of US states (pass figure options to this initial plot):
    figure = df_states.plot_bokeh(
        figsize=(900, 600),
        simplify_shapes=5000,
        slider=slider_columns,
        slider_range=slider_range,
        slider_name="Year",
        colormap="Inferno",
        hovertool_columns=["STATE_NAME"] + slider_columns,
        title="Change of Population [%]",
        show_figure=False,
    )

    # Plot cities as points on top of the US states layer by passing the figure:
    html_multilayer_slider = df_cities.plot_bokeh(
        figure=figure,  # <== pass figure here!
        category="pop_max",
        colormap="Viridis",
        colormap_uselog=True,
        size="size",
        hovertool_string="""<h1>@name</h1>
                            <h3>Population: @pop_max </h3>""",
        marker="inverted_triangle",
        legend="Cities",
        show_figure=False,
        return_html=True,
    )

    with open(
        os.path.join(directory, "Plots", "Multiple_Geolayers_Slider.html"), "w"
    ) as f:
        f.write(html_multilayer_slider)

#     assert False  # ASSERT IS FALSE BECAUSE SLIDER IS NOT VISIBLE RIGHT NOW:


def test_hole_geplot():
    "Tests for (multi-)polygones with holes."

    df = gpd.GeoDataFrame.from_file(
        os.path.join(directory, '../Documentation/Testdata/hole_shapes/hole_shapes.geojson')
    )
    figure = df.plot_bokeh(show_figure=False)

    with open(
        os.path.join(directory, "Plots", "Geolayers_Multipolygons_Holes.html"), "w"
    ) as f:
        f.write(pandas_bokeh.embedded_html(figure))

    assert True
