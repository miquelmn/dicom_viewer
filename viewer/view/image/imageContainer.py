# -*- coding: utf-8 -*-
""" Tkinter frame to contain an image.

"""
from typing import List
import tkinter as tk
from . import canvasHistogram, canvasimage
import numpy as np


class ContainerImage(tk.Frame):
    __pixel_value_fixed = "Valor de píxel: "
    __distance_value_fixed = " Distància: "

    def __init__(self, parent, histogram=True, **kwargs):
        super().__init__(parent, **kwargs)

        self.__img_size = (400, 400)
        self.__canvas_image = canvasimage.CanvasImage(parent=self, row=0, column=0,
                                                      size=self.__img_size)

        if histogram:
            self.__canvas_histogram = canvasHistogram.CanvasHistogram(parent=self, row=2, column=0,
                                                                      size=self.__img_size)
        else:
            self.__canvas_histogram = None

        self.__n_images = 1
        self.__scale_depth = None
        self.__scale_zoom = None
        self.__label_pixel = None

        self.__pixel_value = ""
        self.__distance_value = ""

        self.__f_depth = None
        self.__f_zoom = None

    @property
    def depth(self):
        """ Returns the selected depth of the GUI.

        Returns:

        """
        dep = 0
        if self.__scale_depth is not None:
            dep = self.__scale_depth.get()

        return dep

    def set_n_images(self, value: int):
        """ Sets maximum depth of 3D image.

        Args:
            value:

        Returns:

        """
        self.__n_images = value
        if self.__scale_depth is not None:
            self.__scale_depth.configure(to=value)

    def set_functions(self, movements, depth, zoom, histogram, histogram_release, pixel_value,
                      distance):
        """ Set the listener of the events.

        Args:
            movements:
            depth:
            zoom:
            histogram:
            histogram_release:
            pixel_value:
            distance:

        Returns:

        """
        self.__canvas_image.set_function(
            {"<Button-1>": movements[0], "<ButtonRelease-1>": movements[1],
             pixel_value[0]: pixel_value[1], distance[0]: distance[1]})
        self.__canvas_histogram.set_function(
            {"<B1-Motion>": histogram, "<ButtonRelease-1>": histogram_release})
        self.__f_depth = depth
        self.__f_zoom = zoom

    def draw(self):
        frame_img = self

        self.__scale_depth = tk.Scale(frame_img, from_=0, to=1, orient=tk.HORIZONTAL,
                                      command=self.__f_depth)
        self.__scale_depth.grid(row=3, column=0, sticky="nsew")

        self.__scale_zoom = tk.Scale(frame_img, from_=1, to=1, command=self.__f_zoom)
        self.__scale_zoom.grid(row=0, column=2, sticky="nsew", rowspan=2)

        self.__label_pixel = tk.Label(frame_img, anchor="nw",
                                      text=self.__get_label_text())
        self.__label_pixel.grid(row=1, column=0, sticky="W")

        frame_img.grid(row=0, column=1, sticky="nsew")

        self.__canvas_image.draw()

        if self.__canvas_histogram is not None:
            self.__canvas_histogram.draw()

    @property
    def img_space(self):
        return self.__img_size

    def update_image(self, img: np.ndarray, histogram=None):
        self.__canvas_image.show_image(img)
        self.__scale_zoom.configure(to=100)

        if histogram is not None:
            self.__canvas_histogram.show_image(histogram)

    def move_histogram_line(self, id_line: int, front: bool, velocity: int):
        self.__canvas_histogram.move_line(id_line, front, velocity)

    def lines_position(self):
        return list(self.__canvas_histogram.lines_bb())

    def get_image_position(self) -> List[int]:
        return self.__canvas_image.get_bbox()

    def get_histogram_position(self) -> List[int]:
        return self.__canvas_histogram.get_bbox()

    def set_text_value(self, value: str):
        self.__pixel_value = value

        self.__label_pixel["text"] = self.__get_label_text()

    def set_distance_value(self, value: str):
        self.__distance_value = value

        self.__label_pixel["text"] = self.__get_label_text()

    def __get_label_text(self) -> str:
        return self.__pixel_value_fixed + self.__pixel_value + self.__distance_value_fixed + \
               self.__distance_value
