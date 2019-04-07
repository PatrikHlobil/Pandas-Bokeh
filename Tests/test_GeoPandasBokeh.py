import json
import pandas as pd
import geopandas as gpd
import numpy as np
import pandas_bokeh
import os

directory = os.path.dirname(__file__)
os.makedirs(os.path.join(directory, "Plots"), exist_ok=True)

# def test_geolayers_simple():
#     "Tests for mutiple geolayers"


#     # Read in GeoJSON from URL:
#     df_states = gpd.read_file(
#         r"https://raw.githubusercontent.com/PatrikHlobil/Pandas-Bokeh/master/Documentation/Testdata/states/states.geojson"
#     )
#     gdf = gpd.read_file(
#         r"https://raw.githubusercontent.com/PatrikHlobil/Pandas-Bokeh/master/Documentation/Testdata/populated%20places/ne_10m_populated_places_simple_bigcities.geojson"
#     )
#     gdf["size"] = gdf.pop_max / 400000

#     figure = df_states.plot_bokeh(simplify_shapes=10000, show_figure=False)
#     p_multilayer = gdf.plot_bokeh(
#         figure=figure,
#         category="pop_max",
#         colormap="Viridis",
#         colormap_uselog=True,
#         size="size",
#         hovertool_string="""<h1>@name</h1>
#                             <h3>Population: @pop_max </h3>""",
#         xlim=[-15, 35],
#         ylim=[30, 60],
#         marker="inverted_triangle",
#         show_figure=False,
#     )

#     with open(
#         os.path.join(directory, "Plots", "Multiple_Geolayers_Simple.html"), "w"
#     ) as f:
#         f.write(pandas_bokeh.embedded_html(p_multilayer))

#     assert True


# def test_geolayers_slider():
#     "Tests for mutiple geolayers"

#     # Read in GeoJSON from URL:
#     df_states = gpd.read_file(
#         r"https://raw.githubusercontent.com/PatrikHlobil/Pandas-Bokeh/master/Documentation/Testdata/states/states.geojson"
#     )
#     gdf = gpd.read_file(
#         r"https://raw.githubusercontent.com/PatrikHlobil/Pandas-Bokeh/master/Documentation/Testdata/populated%20places/ne_10m_populated_places_simple_bigcities.geojson"
#     )
#     gdf["size"] = gdf.pop_max / 400000

#     # Calculate change of population relative to 2010:
#     for i in range(8):
#         df_states["Delta_Population_201%d" % i] = (
#             (df_states["POPESTIMATE201%d" % i] / df_states["POPESTIMATE2010"]) - 1
#         ) * 100

#     # Specify slider columns:
#     slider_columns = ["Delta_Population_201%d" % i for i in range(8)]

#     # Specify slider-range (Maps "Delta_Population_2010" -> 2010,
#     #                           "Delta_Population_2011" -> 2011, ...):
#     slider_range = range(2010, 2018)

#     # Make slider plot:
#     figure = df_states.plot_bokeh(
#         figsize=(900, 600),
#         simplify_shapes=5000,
#         slider=slider_columns,
#         slider_range=slider_range,
#         slider_name="Year",
#         colormap="Inferno",
#         hovertool_columns=["STATE_NAME"] + slider_columns,
#         title="Change of Population [%]",
#         show_figure=False,
#     )

#     p_multilayer_slider = gdf.plot_bokeh(
#         figure=figure,
#         category="pop_max",
#         colormap="Viridis",
#         colormap_uselog=True,
#         size="size",
#         hovertool_string="""<h1>@name</h1>
#                             <h3>Population: @pop_max </h3>""",
#         xlim=[-15, 35],
#         ylim=[30, 60],
#         marker="inverted_triangle",
#         show_figure=False,
#     )

#     with open(
#         os.path.join(directory, "Plots", "Multiple_Geolayers_Slider.html"), "w"
#     ) as f:
#         f.write(pandas_bokeh.embedded_html(p_multilayer_slider))

#     assert False  # ASSERT IS FALSE BECAUSE SLIDER IS NOT VISIBLE RIGHT NOW: