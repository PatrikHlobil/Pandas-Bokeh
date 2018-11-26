# TODO: Do not define new figure if figure is provided by user (plot several glyphs on the same graph)
# TODO: Change Legend title when selecting new column in dropdown (in CustomJS)
# TODO: Implement xrange, yrange
# TODO: Doc-String
# TODO: GMaps Tile provider
# TODO: Also keep kwarg columns, if they are in geodataframe (then it is possible to use e.g. column values for the width or alpha value of lines ...)


import numbers

import numpy as np
from collections import OrderedDict
from collections.abc import Iterable 
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import (HoverTool, LogColorMapper, LinearColorMapper,
                          GeoJSONDataSource, WheelZoomTool, ColorBar,
                          BasicTicker,LogTicker, Dropdown, Slider, 
                          ColumnDataSource)
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Dropdown
from bokeh.palettes import all_palettes
from bokeh.colors import RGB
from bokeh.layouts import row, column

from .base import embedded_html

blue_colormap = [RGB(255-i, 255-i, 255) for i in range(256)]

def _add_backgroundtile(p, tile_provider, tile_provider_url):
    """Add a background tile to the plot. Either uses predefined Tiles from Bokeh 
    (parameter: tile_provider) or user passed a tile_provider_url of the form 
    '<url>/{Z}/{X}/{Y}*.png'."""

    from bokeh.tile_providers import (CARTODBPOSITRON, CARTODBPOSITRON_RETINA,
                                  STAMEN_TERRAIN, STAMEN_TERRAIN_RETINA,
                                  STAMEN_TONER, STAMEN_TONER_BACKGROUND,
                                  STAMEN_TONER_LABELS)
    from bokeh.models import WMTSTileSource
    
    tile_dict = {
    "CARTODBPOSITRON": CARTODBPOSITRON,
    "CARTODBPOSITRON_RETINA": CARTODBPOSITRON_RETINA,
    "STAMEN_TERRAIN": STAMEN_TERRAIN,
    "STAMEN_TERRAIN_RETINA": STAMEN_TERRAIN_RETINA,
    "STAMEN_TONER": STAMEN_TONER,
    "STAMEN_TONER_BACKGROUND": STAMEN_TONER_BACKGROUND,
    "STAMEN_TONER_LABELS": STAMEN_TONER_LABELS
    }
    
    if not isinstance(tile_provider_url, type(None)):
        if "/{Z}/{X}/{Y}" not in tile_provider_url:
            raise ValueError(
                "<tile_provider_url> has to be of the form '<url>/{Z}/{X}/{Y}*.png'."
            )
        p.add_tile(WMTSTileSource(url=tile_provider_url))

    elif not isinstance(tile_provider, type(None)):
        if not isinstance(tile_provider, str):
            raise ValueError("<tile_provider> only accepts the values: %s" %
                             tile_dict.keys())
        elif tile_provider.upper() in tile_dict:
            p.add_tile(tile_dict[tile_provider])
        else:
            raise ValueError("<tile_provider> only accepts the values: %s" %
                             tile_dict.keys())

    return p


def geoplot(gdf_in,
            fig=None,
            figsize=None,
            title="",
            xlabel="Longitude",
            ylabel="Latitude",
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
            xrange=None,
            yrange=None,
            hovertool=True,
            hovertool_columns=[],
            simplify_shapes=None,
            tile_provider="CARTODBPOSITRON_RETINA",
            tile_provider_url=None,
            toolbar_location=None,
            show_figure=True,
            return_figure=True,
            return_html=False,
            legend=True,
            **kwargs):
    """Doc-String: TODO"""
    
    gdf = gdf_in.copy()

    #Check layertypes:
    layertypes = []
    if "Point" in str(gdf.geom_type.unique()):
        layertypes.append("Point")
    if "Line" in str(gdf.geom_type.unique()):
        layertypes.append("Line")
    if "Polygon" in str(gdf.geom_type.unique()):
        layertypes.append("Polygon")
    if len(layertypes) > 1:
        raise Exception(
            "Can only plot GeoDataFrames/Series with single type of geometry (either Point, Line or Polygon). Provided is a GeoDataFrame/Series with types: %s"
            % layertypes)

    #Get and check provided parameters for geoplot:
    figure_options = {
        "title": title,
        "x_axis_label": xlabel,
        "y_axis_label": ylabel,
        "plot_width": 600,
        "plot_height": 400,
        "toolbar_location": toolbar_location,
        "active_scroll": "wheel_zoom"
    }
    if not isinstance(figsize, type(None)):
        width, height = figsize
        figure_options["plot_width"] = width
        figure_options["plot_height"] = height

    if not isinstance(fig, type(None)):
        raise NotImplementedError("Parameter <figure> not yet implemented.")

    #Convert GeoDataFrame to Web Mercador Projection:
    gdf.to_crs({'init': 'epsg:3857'}, inplace=True)

    #Simplify shapes if wanted:
    if isinstance(simplify_shapes, numbers.Number):
        if layertypes[0] in ["Line", "Polygon"]:
            gdf["geometry"] = gdf["geometry"].simplify(simplify_shapes)
    elif not isinstance(simplify_shapes, type(None)):
        raise ValueError(
            "<simplify_shapes> parameter only accepts numbers or None.")

    #Check for category, dropdown or slider (choropleth map column):
    category_options = 0
    if not isinstance(category, type(None)):
        category_options += 1
        category_columns = [category]
    if not isinstance(dropdown, type(None)):
        category_options += 1
        category_columns = dropdown
    if not isinstance(slider, type(None)):
        category_options += 1
        category_columns = slider
    if category_options > 1:
        raise ValueError(
            "Only one of <category>, <dropdown> or <slider> parameters is allowed to be used at once."
        )

    #Check for category (single choropleth plot):
    if isinstance(category, type(None)):
        pass
    elif isinstance(category, (list, tuple)):
        raise ValueError(
            "For <category>, please provide an existing single column of the GeoDataFrame."
        )
    elif category in gdf.columns:
        pass
    else:
        raise ValueError(
            "Could not find column '%s' in GeoDataFrame. For <category>, please provide an existing single column of the GeoDataFrame."
            % category)

    #Check for dropdown (multiple choropleth plots via dropdown selection):
    if isinstance(dropdown, type(None)):
        pass
    elif not isinstance(dropdown, (list, tuple)):
        raise ValueError(
            "For <dropdown>, please provide a list/tuple of existing columns of the GeoDataFrame."
        )
    else:
        for col in dropdown:
            if col not in gdf.columns:
                raise ValueError(
                    "Could not find column '%s' for <dropdown> in GeoDataFrame. "
                    % col)

    #Check for slider (multiple choropleth plots via slider selection):                
    if isinstance(slider, type(None)):
        pass
    elif not isinstance(slider, (list, tuple)):
        raise ValueError(
            "For <slider>, please provide a list/tuple of existing columns of the GeoDataFrame."
        )
    else:
        for col in slider:
            if col not in gdf.columns:
                raise ValueError(
                    "Could not find column '%s' for <slider> in GeoDataFrame. "
                    % col) 
        
        if not isinstance(slider_range, type(None)):
            if not isinstance(slider_range, Iterable):
                raise ValueError(
                    "<slider_range> has to be a type that is iterable like list, tuple, range, ...")
            else:
                slider_range = list(slider_range)
                if len(slider_range) != len(slider):
                    raise ValueError("The number of elements in <slider_range> has to be the same as in <slider>.")
                steps = []
                for i in range(len(slider_range)-1):
                    steps.append(slider_range[i+1] - slider_range[i])
                    
                if len(set(steps)) > 1:
                    raise ValueError("<slider_range> has to have equal step size between each elements (like a range-object).")
                else:
                    slider_step = steps[0]
                    slider_start = slider_range[0]
                    slider_end = slider_range[-1]
                
    #Check colormap if either <category>, <dropdown> or <slider> is choosen:
    if category_options == 1:
        if isinstance(colormap, type(None)):
            colormap = blue_colormap
        elif isinstance(colormap, (tuple, list)):
            if len(colormap) > 1:
                pass
            else:
                raise ValueError("<colormap> only accepts a list/tuple of at least two colors or the name of one of the following predefined colormaps (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): %s"%(list(all_palettes.keys())))
        elif isinstance(colormap, str):
            if colormap in all_palettes:
                colormap = all_palettes[colormap]
                colormap = colormap[max(colormap.keys())]
            else:
                raise ValueError("Could not find <colormap> with name %s. The following predefined colormaps are supported (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): %s"%(colormap, list(all_palettes.keys())))
        else:
            raise ValueError("<colormap> only accepts a list/tuple of at least two colors or the name of one of the following predefined colormaps (see also https://bokeh.pydata.org/en/latest/docs/reference/palettes.html ): %s"%(list(all_palettes.keys())))
    else:
        if isinstance(color, str):
            colormap = [color]
        else:
            raise ValueError("<color> has to be a string specifying the fill_color of the map glyph.")
            
            
    #Create Figure to draw:
    if "Point" in layertypes or "Line" in layertypes:
        figure_options["output_backend"] = "webgl"
    p = figure(
        x_axis_type="mercator", y_axis_type="mercator", **figure_options)

    #Get ridd of zoom on axes:
    for t in p.tools:
        if type(t) == WheelZoomTool:
            t.zoom_on_axis = False

    #Add Tile Source as Background:
    p = _add_backgroundtile(p, tile_provider, tile_provider_url)

    # Hide legend if wanted:
    if not legend:
        p.legend.visible = False
    legend = "GeoLayer"
    
    #Define colormapper:
    if len(colormap) == 1:
        kwargs["fill_color"] = colormap[0]

    elif not isinstance(category, type(None)):
        #Check if category column is numerical:
        if not issubclass(gdf[category].dtype.type, np.number):
            raise NotImplementedError("<category> plot only yet implemented for numerical columns. Column '%s' is not numerical."%category)

        field = category
        colormapper_options = {"palette": colormap}
        if not isinstance(colormap_range, type(None)):
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError("<colormap_range> can only be 'None' or a tuple/list of form (min, max).")
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
        kwargs["fill_color"] = {'field': "Colormap",
                                'transform': colormapper}
        legend = str(field)

    elif not isinstance(dropdown, type(None)):
        #Check if all columns in dropdown selection are numerical:
        for col in dropdown:
            if not issubclass(gdf[col].dtype.type, np.number):
                raise NotImplementedError("<dropdown> plot only yet implemented for numerical columns. Column '%s' is not numerical."%col)

        field = dropdown[0]
        colormapper_options = {"palette": colormap}
        if not isinstance(colormap_range, type(None)):
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError("<colormap_range> can only be 'None' or a tuple/list of form (min, max).")
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
        kwargs["fill_color"] = {'field': "Colormap",
                                'transform': colormapper}
        legend = "Geolayer" ##str(field)
        
    elif not isinstance(slider, type(None)):
        #Check if all columns in dropdown selection are numerical:
        for col in slider:
            if not issubclass(gdf[col].dtype.type, np.number):
                raise NotImplementedError("<slider> plot only yet implemented for numerical columns. Column '%s' is not numerical."%col)

        field = slider[0]
        colormapper_options = {"palette": colormap}
        if not isinstance(colormap_range, type(None)):
            if not isinstance(colormap_range, (tuple, list)):
                raise ValueError("<colormap_range> can only be 'None' or a tuple/list of form (min, max).")
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
        kwargs["fill_color"] = {'field': "Colormap",
                                'transform': colormapper}
        legend = "Geolayer" ##str(field)

    #Check for Hovertool columns:
    if hovertool:
        if not isinstance(hovertool_columns, (list, tuple)):
            if hovertool_columns == "all":
                hovertool_columns = list(filter(lambda col: col != "geometry", df_shapes.columns))
            else:
                raise ValueError("<hovertool_columns> has to be a list of columns of the GeoDataFrame or the string 'all'.")
        elif len(hovertool_columns) == 0:
            if not isinstance(category, type(None)):
                hovertool_columns = [category]
            elif not isinstance(dropdown, type(None)):
                hovertool_columns = dropdown
            elif not isinstance(slider, type(None)):
                hovertool_columns = slider
            else:
                hovertool_columns = []
        else:
            for col in hovertool_columns:
                if col not in gdf.columns:
                    raise ValueError("Could not find columns '%s' in GeoDataFrame. <hovertool_columns> has to be a list of columns of the GeoDataFrame or the string 'all'."%col)
    else:
        if isinstance(category, type(None)):
            hovertool_columns = []
        else:
            hovertool_columns = [category]

    #Reduce DataFrame to needed columns:
    if category_options == 0:
        gdf = gdf[hovertool_columns + ["geometry"]]
    else:
        gdf = gdf[list(set(hovertool_columns)|set(category_columns)) + ["geometry"]]
        gdf["Colormap"] = gdf[field]
        field = "Colormap"
    
    #Create GeoJSON DataSource for Plot:
    geo_source = GeoJSONDataSource(geojson=gdf.to_json())
    
    
    #Draw Glyph on Figure:
    layout = None
    if "Point" in layertypes:
        if "line_color" not in kwargs:
            kwargs["line_color"] = kwargs["fill_color"]
        p.scatter(x="x", y="y", source=geo_source, legend=legend, **kwargs)

    if "Line" in layertypes:
        if "line_color" not in kwargs:
            kwargs["line_color"] = kwargs["fill_color"]
        p.multi_line(xs="xs", ys="ys", source=geo_source, legend=legend, **kwargs)

    if "Polygon" in layertypes:
        
        if "line_color" not in kwargs:
            kwargs["line_color"] = "black"

        #Plot polygons:
        p.patches(xs="xs", ys="ys", source=geo_source, legend=legend, **kwargs)

    if hovertool and (category_options == 1 or len(hovertool_columns)>0):
        my_hover = HoverTool()
        my_hover.tooltips = [(str(col), "@{%s}"%col) for col in hovertool_columns]
        p.add_tools(my_hover)

    if show_colorbar and category_options == 1:
        colorbar_options = {"color_mapper": colormapper,
                            "label_standoff": 12,
                            "border_line_color": None,
                            "location": (0,0)}
        if colormap_uselog:
            colorbar_options["ticker"] = LogTicker()

        colorbar = ColorBar(**colorbar_options)

        p.add_layout(colorbar, "right")

    if not isinstance(dropdown, type(None)):
        #Define Dropdown widget:
        dropdown_widget = Dropdown(label="Select Choropleth Layer", 
                                   menu=list(zip(dropdown, dropdown)))

        #Define Callback for Dropdown widget:
        callback = CustomJS(args=dict(dropdown_widget=dropdown_widget,
                                      geo_source=geo_source,
                                      p=p),
                            code="""

                //Change selection of field for Colormapper for choropleth plot:
                geo_source.data["Colormap"] = geo_source.data[dropdown_widget.value];
                geo_source.change.emit();
                //p.legend[0].items[0]["label"] = dropdown_widget.value;

                            """)
        dropdown_widget.js_on_change("value", callback)
        
        #Add Dropdown widget above the plot:
        layout = column(dropdown_widget, p)
        
    if not isinstance(slider, type(None)):
        
        if slider_range is None:
            slider_start = 0
            slider_end = len(slider) - 1
            slider_step = 1
        
        value2name = ColumnDataSource(
                        {"Values": np.arange(slider_start, slider_end+slider_step, slider_step),
                         "Names": slider})
        
        #Define Slider widget:
        slider_widget = Slider(start=slider_start, end=slider_end, value=slider_start, 
                               step=slider_step, title=slider_name)
        
        #Define Callback for Slider widget:
        callback = CustomJS(args=dict(slider_widget=slider_widget,
                                      geo_source=geo_source,
                                      value2name=value2name,
                                      ),
                            code="""

                //Change selection of field for Colormapper for choropleth plot:
                var slider_value = slider_widget.value;
                for(i=0; i<value2name.data["Names"].length; i++)
                    {
                    if (value2name.data["Values"][i] == slider_value)
                        {
                         var name = value2name.data["Names"][i];
                         }

                    }
                geo_source.data["Colormap"] = geo_source.data[name];
                geo_source.change.emit();

                            """)
        slider_widget.js_on_change("value", callback)
        
        #Add Slider widget above the plot:
        layout = column(slider_widget, p)
        
            
    # Set click policy for legend:
    p.legend.click_policy = "hide"

    # Display plot and if wanted return plot:
    if isinstance(layout, type(None)):
        layout = p

    # Display plot if wanted
    if show_figure:
        show(layout)

    #Return as (embeddable) HTML if wanted:
    if return_html:
        return embedded_html(layout)
        
    #Return plot:
    if return_figure:
        return layout


