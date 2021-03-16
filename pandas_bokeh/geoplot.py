import numbers
from collections.abc import Hashable, Iterable

import numpy as np
import pandas as pd
from bokeh.colors import RGB
from bokeh.models import NumeralTickFormatter, TickFormatter
from bokeh.tile_providers import get_provider

from .base import embedded_html

blue_colormap = [RGB(255 - i, 255 - i, 255) for i in range(256)]

TILE_PROVIDERS = [
    "CARTODBPOSITRON",
    "CARTODBPOSITRON_RETINA",
    "STAMEN_TERRAIN",
    "STAMEN_TERRAIN_RETINA",
    "STAMEN_TONER",
    "STAMEN_TONER_BACKGROUND",
    "STAMEN_TONER_LABELS",
    "OSM",
    "WIKIMEDIA",
    "ESRI_IMAGERY",
]


def _get_background_tile(provider_name):
    """Returns a Bokeh WTMS Tile Provider Source from <provider_name>. If
    <provider_name is not valid, it returns False."""

    if provider_name not in TILE_PROVIDERS:
        return False

    return get_provider(provider_name)


def _add_backgroundtile(
    p, tile_provider, tile_provider_url, tile_attribution, tile_alpha
):
    """Add a background tile to the plot. Either uses predefined Tiles from Bokeh
    (parameter: tile_provider) or user passed a tile_provider_url of the form
    '<url>/{Z}/{X}/{Y}*.png' or '<url>/{Z}/{Y}/{X}*.png'."""

    from bokeh.models import WMTSTileSource

    if tile_provider_url is not None:
        if (
            "/{Z}/{X}/{Y}" not in tile_provider_url
            and "/{Z}/{Y}/{X}" not in tile_provider_url
        ):
            raise ValueError(
                "<tile_provider_url> has to be of the form '<url>/{Z}/{X}/{Y}*.png' or <url>/{Z}/{Y}/{X}*.png'."
            )
        if not isinstance(tile_attribution, str):
            raise ValueError("<tile_attribution> has to be a string.")
        t = p.add_tile(
            WMTSTileSource(url=tile_provider_url, attribution=tile_attribution)
        )
        t.alpha = tile_alpha

    elif tile_provider is not None:
        if not isinstance(tile_provider, str):
            raise ValueError(
                f"<tile_provider> only accepts the values: {TILE_PROVIDERS}"
            )
        elif _get_background_tile(tile_provider):
            t = p.add_tile(_get_background_tile(tile_provider))
        else:
            raise ValueError(
                f"<tile_provider> only accepts the values: {TILE_PROVIDERS}"
            )
        t.alpha = tile_alpha

    return p


def _get_figure(col):
    """Gets the bokeh.plotting.figure from a bokeh.layouts.column."""

    from bokeh.layouts import column
    from bokeh.plotting import figure

    for children in col.children:
        if isinstance(children, type(figure())):
            return children
        elif isinstance(children, type(column())):
            return _get_figure(children)


def convert_geoDataFrame_to_patches(gdf, geometry_column):
    """Creates from a geoDataFrame with Polygons and Multipolygons a Pandas DataFrame
    with x any y columns specifying the geometry of the Polygons."""

    df_new = []

    def add_x_and_y_columns(row, geometry):
        row = row.copy()
        x, y = geometry.exterior.xy

        # Convert to int for web mercador projection to save space:
        row["__x__"] = [[[int(_) for _ in x]]]
        row["__y__"] = [[[int(_) for _ in y]]]

        for interior in geometry.interiors:
            x, y, *z = zip(*interior.coords)
            row["__x__"][0].append([int(_) for _ in x])
            row["__y__"][0].append([int(_) for _ in y])

        return row

    for i, row in gdf.iterrows():
        geometry = row[geometry_column]
        if geometry.type == "Polygon":
            df_new.append(add_x_and_y_columns(row, geometry))

        if geometry.type == "MultiPolygon":
            for polygon in geometry:
                df_new.append(add_x_and_y_columns(row, polygon))

    df_new = pd.DataFrame(df_new)

    df_new = df_new.drop(columns=[geometry_column])
    return df_new


def get_tick_formatter(formatter_arg):

    if issubclass(formatter_arg.__class__, TickFormatter):
        return formatter_arg
    elif isinstance(formatter_arg, str):
        return NumeralTickFormatter(format=formatter_arg)
    else:
        raise ValueError(
            "<colorbar_tick_format> parameter only accepts a string or a objects of bokeh.models.formatters."
        )


def geoplot(  # noqa C901
    gdf_in,
    geometry_column="geometry",
    figure=None,
    figsize=None,
    title="",
    xlabel="Longitude",
    ylabel="Latitude",
    xlim=None,
    ylim=None,
    color="blue",
    colormap=None,
    colormap_uselog=False,
    colormap_range=None,
    category=None,
    dropdown=None,
    slider=None,
    slider_range=None,
    slider_name="",
    show_colorbar=True,
    colorbar_tick_format=None,
    xrange=None,
    yrange=None,
    hovertool=True,
    hovertool_columns=[],
    hovertool_string=None,
    simplify_shapes=None,
    tile_provider="CARTODBPOSITRON_RETINA",
    tile_provider_url=None,
    tile_attribution="",
    tile_alpha=1,
    panning=True,
    zooming=True,
    toolbar_location="right",
    show_figure=True,
    return_figure=True,
    return_html=False,
    legend=True,
    webgl=True,
    **kwargs,
):
    """Doc-String: TODO"""

    # Imports:
    import bokeh.plotting
    from bokeh.layouts import column, row
    from bokeh.models import (
        BasicTicker,
        BoxZoomTool,
        ColorBar,
        ColumnDataSource,
        GeoJSONDataSource,
        HoverTool,
        LinearColorMapper,
        LogColorMapper,
        LogTicker,
        Select,
        Slider,
        WheelZoomTool,
    )
    from bokeh.models.callbacks import CustomJS
    from bokeh.models.widgets import Dropdown
    from bokeh.palettes import all_palettes
    from bokeh.plotting import show

    # Make a copy of the input geodataframe:
    gdf = gdf_in.copy()

    # Check layertypes:
    if type(gdf) != pd.DataFrame:
        layertypes = []
        if "Point" in str(gdf.geom_type.unique()):
            layertypes.append("Point")
        if "Line" in str(gdf.geom_type.unique()):
            layertypes.append("Line")
        if "Polygon" in str(gdf.geom_type.unique()):
            layertypes.append("Polygon")
        if len(layertypes) > 1:
            raise Exception(
                f"Can only plot GeoDataFrames/Series with single type of geometry (either Point, Line or Polygon). Provided is a GeoDataFrame/Series with types: {layertypes}"
            )
    else:
        layertypes = ["Point"]

    # Get and check provided parameters for geoplot:
    figure_options = {
        "title": title,
        "x_axis_label": xlabel,
        "y_axis_label": ylabel,
        "plot_width": 600,
        "plot_height": 400,
        "toolbar_location": toolbar_location,
        "active_scroll": "wheel_zoom",
        "x_axis_type": "mercator",
        "y_axis_type": "mercator",
        "match_aspect": True,
    }
    if figsize is not None:
        width, height = figsize
        figure_options["plot_width"] = width
        figure_options["plot_height"] = height
    if webgl:
        figure_options["output_backend"] = "webgl"

    if type(gdf) != pd.DataFrame:
        # Convert GeoDataFrame to Web Mercator Projection:
        gdf.to_crs(epsg=3857, inplace=True)

        # Simplify shapes if wanted:
        if isinstance(simplify_shapes, numbers.Number):
            if layertypes[0] in ["Line", "Polygon"]:
                gdf[geometry_column] = gdf[geometry_column].simplify(simplify_shapes)
        elif simplify_shapes is not None:
            raise ValueError(
                "<simplify_shapes> parameter only accepts numbers or None."
            )

    # Check for category, dropdown or slider (choropleth map column):
    category_options = 0
    if category is not None:
        category_options += 1
        category_columns = [category]
    if dropdown is not None:
        category_options += 1
        category_columns = dropdown
    if slider is not None:
        category_options += 1
        category_columns = slider
    if category_options > 1:
        raise ValueError(
            "Only one of <category>, <dropdown> or <slider> parameters is allowed to be used at once."
        )

    # Check for category (single choropleth plot):
    if category is None:
        pass
    elif isinstance(category, (list, tuple)):
        raise ValueError(
            "For <category>, please provide an existing single column of the GeoDataFrame."
        )
    elif category in gdf.columns:
        pass
    else:
        raise ValueError(
            f"Could not find column '{category}' in GeoDataFrame. For <category>, please provide an existing single column of the GeoDataFrame."
        )

    # Check for dropdown (multiple choropleth plots via dropdown selection):
    if dropdown is None:
        pass
    elif not isinstance(dropdown, (list, tuple)):
        raise ValueError(
            "For <dropdown>, please provide a list/tuple of existing columns of the GeoDataFrame."
        )
    else:
        for col in dropdown:
            if col not in gdf.columns:
                raise ValueError(
                    f"Could not find column '{col}' for <dropdown> in GeoDataFrame. "
                )

    # Check for slider (multiple choropleth plots via slider selection):
    if slider is None:
        pass
    elif not isinstance(slider, (list, tuple)):
        raise ValueError(
            "For <slider>, please provide a list/tuple of existing columns of the GeoDataFrame."
        )
    else:
        for col in slider:
            if col not in gdf.columns:
                raise ValueError(
                    f"Could not find column '{col}' for <slider> in GeoDataFrame. "
                )

        if slider_range is not None:
            if not isinstance(slider_range, Iterable):
                raise ValueError(
                    "<slider_range> has to be a type that is iterable like list, tuple, range, ..."
                )
            else:
                slider_range = list(slider_range)
                if len(slider_range) != len(slider):
                    raise ValueError(
                        "The number of elements in <slider_range> has to be the same as in <slider>."
                    )
                steps = []
                for i in range(len(slider_range) - 1):
                    steps.append(slider_range[i + 1] - slider_range[i])

                if len(set(steps)) > 1:
                    raise ValueError(
                        "<slider_range> has to have equal step size between each elements (like a range-object)."
                    )
                else:
                    slider_step = steps[0]
                    slider_start = slider_range[0]
                    slider_end = slider_range[-1]

    # Check colormap if either <category>, <dropdown> or <slider> is choosen:
    if category_options == 1:
        if colormap is None:
            colormap = blue_colormap
        elif isinstance(colormap, (tuple, list)):
            if len(colormap) > 1:
                pass
            else:
                raise ValueError(
                    f"<colormap> only accepts a list/tuple of at least two colors or the name of one of the following predefined colormaps (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): {list(all_palettes.keys())}"
                )
        elif isinstance(colormap, str):
            if colormap in all_palettes:
                colormap = all_palettes[colormap]
                colormap = colormap[max(colormap.keys())]
            else:
                raise ValueError(
                    f"Could not find <colormap> with name {colormap}. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): {list(all_palettes.keys())}"
                )
        else:
            raise ValueError(
                f"<colormap> only accepts a list/tuple of at least two colors or the name of one of the following predefined colormaps (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): {list(all_palettes.keys())}"
            )
    else:
        if isinstance(color, str):
            colormap = [color]
        elif color is None:
            colormap = ["blue"]
        else:
            raise ValueError(
                "<color> has to be a string specifying the fill_color of the map glyph."
            )

    # Check xlim & ylim:
    if xlim is not None:
        if isinstance(xlim, (tuple, list)):
            if len(xlim) == 2:
                xmin, xmax = xlim
                for _ in [xmin, xmax]:
                    if not -180 < _ <= 180:
                        raise ValueError(
                            "Limits for x-axis (=Longitude) have to be between -180 and 180."
                        )
                if not xmin < xmax:
                    raise ValueError("xmin has to be smaller than xmax.")

                from pyproj import Transformer

                transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
                xmin = transformer.transform(0, xmin)[0]
                xmax = transformer.transform(0, xmax)[0]
                figure_options["x_range"] = (xmin, xmax)
            else:
                raise ValueError(
                    "Limits for x-axis (=Longitude) have to be of form [xmin, xmax] with values between -180 and 180."
                )
        else:
            raise ValueError(
                "Limits for x-axis (=Longitude) have to be of form [xmin, xmax] with values between -180 and 180."
            )
    if ylim is not None:
        if isinstance(ylim, (tuple, list)):
            if len(ylim) == 2:
                ymin, ymax = ylim
                for _ in [ymin, ymax]:
                    if not -90 < _ <= 90:
                        raise ValueError(
                            "Limits for y-axis (=Latitude) have to be between -90 and 90."
                        )
                if not ymin < ymax:
                    raise ValueError("ymin has to be smaller than ymax.")

                from pyproj import Transformer

                transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
                ymin = transformer.transform(ymin, 0)[1]
                ymax = transformer.transform(ymax, 0)[1]
                figure_options["y_range"] = (ymin, ymax)
            else:
                raise ValueError(
                    "Limits for y-axis (=Latitude) have to be of form [ymin, ymax] with values between -90 and 90."
                )
        else:
            raise ValueError(
                "Limits for y-axis (=Latitude) have to be of form [ymin, ymax] with values between -90 and 90."
            )

    # Create Figure to draw:
    old_layout = None
    if figure is None:
        figure_options["x_axis_label"] = (
            figure_options["x_axis_label"]
            if figure_options["x_axis_label"] is not None
            else "Longitute"
        )
        figure_options["y_axis_label"] = (
            figure_options["y_axis_label"]
            if figure_options["y_axis_label"] is not None
            else "Latitude"
        )
        p = bokeh.plotting.figure(**figure_options)

        # Add Tile Source as Background:
        p = _add_backgroundtile(
            p, tile_provider, tile_provider_url, tile_attribution, tile_alpha
        )

    elif isinstance(figure, type(bokeh.plotting.figure())):
        p = figure
    elif isinstance(figure, type(column())):
        old_layout = figure
        p = _get_figure(old_layout)
    else:
        raise ValueError(
            "Parameter <figure> has to be of type bokeh.plotting.figure or bokeh.layouts.column."
        )

    for t in p.tools:
        # Get ridd of zoom on axes:
        if isinstance(t, WheelZoomTool):
            t.zoom_on_axis = False
        # Make sure that box zoom matches aspect:
        if isinstance(t, BoxZoomTool):
            t.match_aspect = True

    # Hide legend if wanted:
    legend_input = legend
    if isinstance(legend, str):
        pass
    else:
        legend = "GeoLayer"

    # Define colormapper:
    if len(colormap) == 1:
        kwargs["fill_color"] = colormap[0]

    elif category is not None:
        # Check if category column is numerical:
        if not issubclass(gdf[category].dtype.type, np.number):
            raise NotImplementedError(
                f"<category> plot only yet implemented for numerical columns. Column '{category}' is not numerical."
            )

        field = category
        colormapper_options = {"palette": colormap}
        if colormap_range is not None:
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError(
                    "<colormap_range> can only be 'None' or a tuple/list of form (min, max)."
                )
            elif len(colormap_range) == 2:
                colormapper_options["low"] = colormap_range[0]
                colormapper_options["high"] = colormap_range[1]
        else:
            colormapper_options["low"] = gdf[field].min()
            colormapper_options["high"] = gdf[field].max()
        if colormap_uselog:
            colormapper = LogColorMapper(**colormapper_options)
        else:
            colormapper = LinearColorMapper(**colormapper_options)
        kwargs["fill_color"] = {"field": "Colormap", "transform": colormapper}
        if not isinstance(legend, str):
            legend = str(field)

    elif dropdown is not None:
        # Check if all columns in dropdown selection are numerical:
        for col in dropdown:
            if not issubclass(gdf[col].dtype.type, np.number):
                raise NotImplementedError(
                    f"<dropdown> plot only yet implemented for numerical columns. Column '{col}' is not numerical."
                )

        field = dropdown[0]
        colormapper_options = {"palette": colormap}
        if colormap_range is not None:
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError(
                    "<colormap_range> can only be 'None' or a tuple/list of form (min, max)."
                )
            elif len(colormap_range) == 2:
                colormapper_options["low"] = colormap_range[0]
                colormapper_options["high"] = colormap_range[1]
        else:
            colormapper_options["low"] = gdf[dropdown].min().min()
            colormapper_options["high"] = gdf[dropdown].max().max()
        if colormap_uselog:
            colormapper = LogColorMapper(**colormapper_options)
        else:
            colormapper = LinearColorMapper(**colormapper_options)
        kwargs["fill_color"] = {"field": "Colormap", "transform": colormapper}
        legend = " " + field

    elif slider is not None:
        # Check if all columns in dropdown selection are numerical:
        for col in slider:
            if not issubclass(gdf[col].dtype.type, np.number):
                raise NotImplementedError(
                    f"<slider> plot only yet implemented for numerical columns. Column '{col}' is not numerical."
                )

        field = slider[0]
        colormapper_options = {"palette": colormap}
        if colormap_range is not None:
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError(
                    "<colormap_range> can only be 'None' or a tuple/list of form (min, max)."
                )
            elif len(colormap_range) == 2:
                colormapper_options["low"] = colormap_range[0]
                colormapper_options["high"] = colormap_range[1]
        else:
            colormapper_options["low"] = gdf[slider].min().min()
            colormapper_options["high"] = gdf[slider].max().max()
        if colormap_uselog:
            colormapper = LogColorMapper(**colormapper_options)
        else:
            colormapper = LinearColorMapper(**colormapper_options)
        kwargs["fill_color"] = {"field": "Colormap", "transform": colormapper}
        if not isinstance(legend, str):
            legend = "Geolayer"

    # Check that only hovertool_columns or hovertool_string is used:
    if isinstance(hovertool_columns, (list, tuple, str)):
        if len(hovertool_columns) > 0 and hovertool_string is not None:
            raise ValueError(
                "Either <hovertool_columns> or <hovertool_string> can be used, but not both at the same time."
            )
    else:
        raise ValueError(
            "<hovertool_columns> has to be a list of columns of the GeoDataFrame or the string 'all'."
        )

    if hovertool_string is not None:
        hovertool_columns = "all"

    # Check for Hovertool columns:
    if hovertool:
        if not isinstance(hovertool_columns, (list, tuple)):
            if hovertool_columns == "all":
                hovertool_columns = list(
                    filter(lambda col: col != geometry_column, gdf.columns)
                )
            else:
                raise ValueError(
                    "<hovertool_columns> has to be a list of columns of the GeoDataFrame or the string 'all'."
                )
        elif len(hovertool_columns) == 0:
            if category is not None:
                hovertool_columns = [category]
            elif dropdown is not None:
                hovertool_columns = dropdown
            elif slider is not None:
                hovertool_columns = slider
            else:
                hovertool_columns = []
        else:
            for col in hovertool_columns:
                if col not in gdf.columns:
                    raise ValueError(
                        f"Could not find columns '{col}' in GeoDataFrame. <hovertool_columns> has to be a list of columns of the GeoDataFrame or the string 'all'."
                    )
    else:
        if category is None:
            hovertool_columns = []
        else:
            hovertool_columns = [category]

    # Reduce DataFrame to needed columns:
    if type(gdf) == pd.DataFrame:
        gdf["Geometry"] = 0
        additional_columns = ["x", "y"]
    else:
        additional_columns = [geometry_column]
    for kwarg, value in kwargs.items():
        if isinstance(value, Hashable):
            if value in gdf.columns:
                additional_columns.append(value)
    if category_options == 0:
        gdf = gdf[list(set(hovertool_columns) | set(additional_columns))]
    else:
        gdf = gdf[
            list(
                set(hovertool_columns) | set(category_columns) | set(additional_columns)
            )
        ]
        gdf["Colormap"] = gdf[field]
        field = "Colormap"

    # Create GeoJSON DataSource for Plot:
    if type(gdf) != pd.DataFrame:
        geo_source = GeoJSONDataSource(geojson=gdf.to_json())
    else:
        geo_source = gdf

    # Draw Glyph on Figure:
    layout = None
    if "Point" in layertypes:
        if "line_color" not in kwargs:
            kwargs["line_color"] = kwargs["fill_color"]
        glyph = p.scatter(
            x="x", y="y", source=geo_source, legend_label=legend, **kwargs
        )

    if "Line" in layertypes:
        if "line_color" not in kwargs:
            kwargs["line_color"] = kwargs["fill_color"]
            del kwargs["fill_color"]
        glyph = p.multi_line(
            xs="xs", ys="ys", source=geo_source, legend_label=legend, **kwargs
        )

    if "Polygon" in layertypes:

        if "line_color" not in kwargs:
            kwargs["line_color"] = "black"

        # Creates from a geoDataFrame with Polygons and Multipolygons a Pandas DataFrame
        # with x any y columns specifying the geometry of the Polygons:
        geo_source = ColumnDataSource(
            convert_geoDataFrame_to_patches(gdf, geometry_column)
        )

        # Plot polygons:
        glyph = p.multi_polygons(
            xs="__x__", ys="__y__", source=geo_source, legend_label=legend, **kwargs
        )

    # Add hovertool:
    if hovertool and (category_options == 1 or len(hovertool_columns) > 0):
        my_hover = HoverTool(renderers=[glyph])
        if hovertool_string is None:
            my_hover.tooltips = [(str(col), "@{%s}" % col) for col in hovertool_columns]
        else:
            my_hover.tooltips = hovertool_string
        p.add_tools(my_hover)

    # Add colorbar:
    if show_colorbar and category_options == 1:
        colorbar_options = {
            "color_mapper": colormapper,
            "label_standoff": 12,
            "border_line_color": None,
            "location": (0, 0),
        }
        if colormap_uselog:
            colorbar_options["ticker"] = LogTicker()

        if colorbar_tick_format:
            colorbar_options["formatter"] = get_tick_formatter(colorbar_tick_format)

        colorbar = ColorBar(**colorbar_options)

        p.add_layout(colorbar, "right")

    # Add Dropdown Widget:
    if dropdown is not None:
        # Define Dropdown widget:
        dropdown_widget = Select(
            title="Select Choropleth Layer", options=list(zip(dropdown, dropdown))
        )

        # Define Callback for Dropdown widget:
        callback = CustomJS(
            args=dict(
                dropdown_widget=dropdown_widget,
                geo_source=geo_source,
                legend=p.legend[0].items[0],
            ),
            code="""

                //Change selection of field for Colormapper for choropleth plot:
                geo_source.data["Colormap"] = geo_source.data[dropdown_widget.value];
                geo_source.change.emit();

                //Change label of Legend:
                legend.label["value"] = " " + dropdown_widget.value;

                            """,
        )
        dropdown_widget.js_on_change("value", callback)

        # Add Dropdown widget above the plot:
        if old_layout is None:
            layout = column(dropdown_widget, p)
        else:
            layout = column(dropdown_widget, old_layout)

    # Add Slider Widget:
    if slider is not None:

        if slider_range is None:
            slider_start = 0
            slider_end = len(slider) - 1
            slider_step = 1

        value2name = ColumnDataSource(
            {
                "Values": np.arange(
                    slider_start, slider_end + slider_step, slider_step
                ),
                "Names": slider,
            }
        )

        # Define Slider widget:
        slider_widget = Slider(
            start=slider_start,
            end=slider_end,
            value=slider_start,
            step=slider_step,
            title=slider_name,
        )

        # Define Callback for Slider widget:
        callback = CustomJS(
            args=dict(
                slider_widget=slider_widget,
                geo_source=geo_source,
                value2name=value2name,
            ),
            code="""

                //Change selection of field for Colormapper for choropleth plot:
                var slider_value = slider_widget.value;
                var i;
                for(i=0; i<value2name.data["Names"].length; i++)
                    {
                    if (value2name.data["Values"][i] == slider_value)
                        {
                         var name = value2name.data["Names"][i];
                         }

                    }
                geo_source.data["Colormap"] = geo_source.data[name];
                geo_source.change.emit();

                            """,
        )
        slider_widget.js_on_change("value", callback)

        # Add Slider widget above the plot:
        if old_layout is None:
            layout = column(slider_widget, p)
        else:
            layout = column(slider_widget, old_layout)

    # Hide legend if user wants:
    if legend_input is False:
        p.legend.visible = False

    # Set click policy for legend:
    p.legend.click_policy = "hide"

    # Set panning option:
    if panning is False:
        p.toolbar.active_drag = None

    # Set zooming option:
    if zooming is False:
        p.toolbar.active_scroll = None

    # Display plot and if wanted return plot:
    if layout is None:
        if old_layout is None:
            layout = p
        else:
            layout = old_layout

    # Display plot if wanted
    if show_figure:
        show(layout)

    # Return as (embeddable) HTML if wanted:
    if return_html:
        return embedded_html(layout)

    # Return plot:
    if return_figure:
        return layout
