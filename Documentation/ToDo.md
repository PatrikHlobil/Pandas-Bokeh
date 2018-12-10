# ToDo List

## Release 0.1:
 
- Add WebGL plotting backend as default (plots and geoplots) ✓
- Replace isinstance(???, None) ✓
- Legend for barplots ✓
- Stacked barplots ✓
- Horizontal barplots ✓
- Show toolbar as standard option ✓
- Add<tile_attribution> parameter for background tiles of geoplots ✓
- Area plots ✓
- Also keep kwarg columns, if they are in geodataframe (then it is possible to use e.g. column values for the width or alpha value of lines ...) for geoplots ✓
- Add dependencies in setup.py ✓
- Histogram standard only on y-axis (don't consider x-axis, but only look at the columns provided by y) ✓
- For Histogram, when creating figure, do not give x_range parameters ✓
- Proper String conversion for barplot with datetimes (look if ms exist, s/m/h exist, ...) --> delete "category" variable? ✓
- Implement xrange, yrange for Geoplots ✓
- For bins, also accept integer values ✓

- For bins, also accept strings with name of bin-autodetection
- Integrate **check_type** function in all places --> Better check for categorical (e.g. multiindex problem --> raise Exception when x-axis is a multiindex)
- Horizontal/Vertical Boxplots
- Pieplot
- Categorical line  & point & area plots (set x = range(N) and define mapping from integers to categorical string representations)
- panning/zooming=True/False parameters implementation
- Change Legend title when selecting new column in dropdown (in CustomJS) for Geoplots
- Docstring Documentation
- Add accessors (df.plot_bokeh(kind="line", ...) == df.plot_bokeh.line(...))
- Grid options (vertical/horizontal/both) for plots
- Check input values of <kind> and throw exception if it doesn't exist

## Release 0.2:
- Proper hovertool for histograms (mabye add invincible lineglyph with hoverinformation)
- refactoring of autodetection of x and y columns for DataFrame.plot_bokeh
- export_options = "bla.png" oder "bla.svg"
- Smarter setting of xticks (do not use all x-values if length of dataframe is too large)
- For Scatterplot, also enable histograms at the side (see https://github.com/bokeh/bokeh/blob/master/examples/app/selection_histogram.py, https://demo.bokehplots.com/apps/selection_histogram)
- Hexbin plots
- **Pandas Bokeh** should be able to produce all plots of Pandas.plot documentation page
- Filter options via slider
- x_axis_format, y_axis_format implementation
- Allow passing a Pandas_Bokeh figure to overlay plot (especially for geoplots)
- GMaps Tile provider for geoplot
- Horizontal Histograms
- Add proper docstrings & only pass relevant keyword arguments for pd.DataFrame.plot_bokeh.line, .bar, .scatter, ... accessors 
- Fix bug when using logscale on y-axis for histograms
- For scatterplot, also show a legend when no category is chosen
- vertical_xlabel should also allow for float values (--> angle )