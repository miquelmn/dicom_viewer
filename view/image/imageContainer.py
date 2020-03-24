from typing import List
import tkinter as tk
from . import canvasHistogram, canvasimage
import numpy as np


class ContainerImage(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # self.__functions = None
        self.__canvas_image = canvasimage.CanvasImage(self, row=0, column=0, size=(600, 400))
        self.__canvas_histogram = canvasHistogram.CanvasHistogram(self, row=1, column=0,
                                                                  size=(680, 480))
        self.__n_images = 1
        self.__scale_depth = None
        self.__scale_zoom = None

        self.__f_depth = None
        self.__f_zoom = None

    def set_n_images(self, value: int):
        self.__n_images = value
        if self.__scale_depth is not None:
            self.__scale_depth.configure(to=value)

    def set_functions(self, movements, depth, zoom, histogram, histogram_release):
        self.__canvas_image.set_function(movements)
        self.__canvas_histogram.set_function(histogram, histogram_release)
        self.__f_depth = depth
        self.__f_zoom = zoom

    def draw(self):
        frame_img = self

        self.__scale_depth = tk.Scale(frame_img, from_=0, to=1, orient=tk.HORIZONTAL,
                                      command=self.__f_depth)
        self.__scale_depth.grid(row=2, column=0, sticky="nsew")

        self.__scale_zoom = tk.Scale(frame_img, from_=1, to=1, command=self.__f_zoom)
        self.__scale_zoom.grid(row=0, column=2, sticky="nsew", rowspan=2)

        frame_img.grid(row=0, column=1, sticky="nsew")

        self.__canvas_image.draw()
        self.__canvas_histogram.draw()

    def update_image(self, img: np.ndarray, histogram=None):
        self.__canvas_image.show_image(img)
        self.__scale_zoom.configure(to=100)

        if histogram is not None:
            self.__canvas_histogram.show_histogram(histogram)

    def move_histogram_line(self, id_line: int, front: bool, velocity: int):
        self.__canvas_histogram.move_line(id_line, front, velocity)

    def lines_position(self):
        return list(self.__canvas_histogram.lines_bb())

    def get_histogram_position(self) -> List[int]:
        return self.__canvas_histogram.get_bbox()
