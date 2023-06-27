from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.sampledata.autompg import autompg as df
import numpy as np

# Prepare the data
hist, edges = np.histogram(df['mpg'], bins=20)

# Create a new plot
p = figure(title="Histogram", background_fill_color="#f9f9f9")

# Add a quad glyph
p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="steelblue", line_color="black")

# Set plot properties
p.xaxis.axis_label = 'MPG'
p.yaxis.axis_label = 'Frequency'

# Save the plot as an HTML file
output_file("histogram.html")

# Display the plot
show(p)
