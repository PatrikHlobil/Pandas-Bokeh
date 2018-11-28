# ToDo List

## Release 0.1:
 
- Add WebGL plotting backend as default (plots and geoplots) ✓
- Integrate **check_type** function in all places --> Better check for categorical (e.g. multiindex problem --> raise Exception when x-axis is a multiindex)
- Replace isinstance(???, None)
- Histogram standard only on y-axis (don't consider x-axis, but only look at the columns provided by y)
- For Histogram, when creating figure, do not give x_range parameters 
- Proper String conversion for barplot with datetimes (look is ms exist, s/m/h exist, ...) --> delete "category" variable?
- Stacked barplots
- Horizontal barplots
- Horizontal/Vertical Boxplots
- Area Plots
- Pieplot
- Show toolbar as standard option (alternatively define a reset button) ✓
- Categorical line  & point plot (set x = range(N) and define mapping from integers to categorical string representations)
- panning/zooming=True/False parameters implementation
- export_options = "bla.png" oder "bla.svg"
- Change Legend title when selecting new column in dropdown (in CustomJS) for Geoplots
- Implement xrange, yrange for Geoplots
- Docstring Documentation
- Also keep kwarg columns, if they are in geodataframe (then it is possible to use e.g. column values for the width or alpha value of lines ...) for geoplots ✓


## Release 0.2:


- For Scatterplot, also enable histograms at the side (see https://github.com/bokeh/bokeh/blob/master/examples/app/selection_histogram.py, https://demo.bokehplots.com/apps/selection_histogram)
- Hexbin plots
- **Pandas Bokeh** should be able to produce all plots of Pandas.plot documenttion page
- Filter options via slider
- x_axis_format, y_axis_format implementation
- Allow passing a Pandas_Bokeh figure to overlay plot (especially for geoplots)
- GMaps Tile provider for geoplots
  