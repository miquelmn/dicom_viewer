from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib import pyplot as plt


def get_histogram(img: np.ndarray):
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.axis('off')
    fig.tight_layout(pad=0)

    # n_bins = min(255, img.max() + (img.min() * -1))

    ax.hist(img.ravel())
    canvas.draw()

    w, h = fig.canvas.get_width_height()
    histogram = np.fromstring(canvas.tostring_rgb(), dtype='uint8')

    histogram = histogram.reshape((h, w, -1))

    return histogram
