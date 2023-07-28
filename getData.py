from bokeh.plotting import figure, show
from bokeh.io import output_file, save
import numpy as np


def processSize(data: list[str, int, int, int]):
    ''' gets size info (data[3]) and creates histogram '''
    sizes = []
    for point in data:
        sizes.append(point[3])

    return sizes

def getSizeHist(data: list[str, int, int, int]):

    sizes = processSize(data)

    # Prepare the data
    hist, edges = np.histogram(sizes, bins=np.logspace(np.log10(min(sizes)), np.log10(max(sizes)), 10))

    # Create a new plot
    p = figure(title="Snowflake Size Histogram", background_fill_color="#fafafa", x_axis_type="log")

    # Add a quad glyph
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="navy", line_color="white", alpha=0.7)


    # Set plot properties
    p.xaxis.axis_label = 'Relative size'
    p.yaxis.axis_label = 'Frequency'

    # Save the plot as an HTML file
    output_file("chosen/data.html")
    save(p)
    #show(p)

def getSnowRateHist(flakes: list[int]):

    # Create a figure
    p = figure(title="Snowflakes Falling Rate", x_axis_label="Time (10-second periods)", y_axis_label="Number of Snowflakes")

    # Prepare x-axis data (time periods)
    x = list(range(1, len(flakes) + 1))

    # Plot the data as a line chart
    p.line(x, flakes, line_width=2)

    output_file("chosen/data2.html")
    save(p)
