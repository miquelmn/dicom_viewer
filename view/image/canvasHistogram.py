from view import view_component
import numpy as np
import tkinter as tk
import functions as funcs
import math


class CanvasHistogram(view_component.VComponent):

    def __init__(self, parent, **kwargs):
        self.__parent = parent

        self.__canvas = None  # Tk.Canvas
        self.__image_on_canvas = None  # Canvas.Create_image
        self.__image_raw = None  # Numpy Array
        self.__image = None  # Tk image

        self.__min_line = None
        self.__max_line = None

        self.__f_histogram = None
        self.__f_release_histogram = None

        super().__init__(**kwargs)

    def set_function(self, histogram, release, **kwargs):
        self.__f_histogram = histogram
        self.__f_release_histogram = release

    def __get_line(self, idx):
        if idx != 0 and idx != 1:
            raise Exception("Index out of bounds")

        if idx == 0:
            return self.__min_line
        elif idx == 1:
            return self.__max_line

    def draw(self, img_raw=None):
        self.__draw_histogram(img_raw)

    def __draw_histogram(self, img_raw):
        if img_raw is None:
            img_raw = np.ones((self._height, self._width)) * 255
        img = super().numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, width=self._width, height=self._height)
        canvas.grid(row=self._row, column=self._column, sticky="nsew")
        image_on_canvas = canvas.create_image(10, 0, anchor="nw", image=img)
        canvas.bind("<B1-Motion>", self.__f_histogram)
        canvas.bind("<ButtonRelease-1>", self.__f_release_histogram)

        self.__image_raw = img_raw
        self.__image = img
        self.__image_on_canvas = image_on_canvas
        self.__canvas = canvas

        self.__create_lines()

    def __create_lines(self):
        assert self.__canvas is not None

        canvas = self.__canvas
        bbox = canvas.bbox(self.__image_on_canvas)

        min_line = canvas.create_line(bbox[0], bbox[1], bbox[0], bbox[3])
        max_line = canvas.create_line(bbox[2], bbox[1], bbox[2], bbox[3])

        self.__min_line = min_line
        self.__max_line = max_line

    def show_histogram(self, histogram: np.ndarray):
        assert self.__image_on_canvas is not None

        pre_bbox = np.array(self.__canvas.bbox(self.__image_on_canvas))
        pre_size = np.array([pre_bbox[2] - pre_bbox[0], pre_bbox[3] - pre_bbox[1]])

        img = CanvasHistogram.numpy_2_tkinter(histogram)
        self.__canvas.itemconfig(self.__image_on_canvas, image=img)
        bbox = np.array(self.__canvas.bbox(self.__image_on_canvas))
        size = np.array([bbox[2] - bbox[0], bbox[3] - bbox[1]])

        if np.linalg.norm((pre_size - size)) > 10:
            self.reset_lines()

        self.__image_raw = histogram
        self.__image = img

    def reset_lines(self):
        bbox = np.array(self.__canvas.bbox(self.__image_on_canvas))

        self.__canvas.coords(self.__max_line, bbox[2], bbox[1], bbox[2], bbox[3] - 1)
        self.__canvas.coords(self.__min_line, bbox[0], bbox[1], bbox[0], bbox[3] - 1)

    def lines_bb(self):
        """
        Yield the bounding box of each line.

        The bounding box is defined by four integers. The couples indicated the top-left point and
        the bottom-right point.

        Returns:

        """
        for i in range(0, 2):
            line = self.__get_line(i)
            yield self.__canvas.bbox(line)

    def move_line(self, id_line: int, back: bool, velocity: int):
        """
        Move the line indicated from the parameter.

        Args:
            id_line (int): If 0 the line moved is the minimum if it's 1 moves the max line
            back (bool): If true the line moves to the right else moves to the left.
            velocity (int): Speed of the movement

        Returns:

        """
        line = self.__get_line(id_line)
        bbox = self.get_bbox()
        maximum = bbox[2]
        minimum = bbox[0]
        pos_line = self.get_bbox(line)

        direction = 1
        if back:
            direction = direction * -1

        if ((not back) and (pos_line[0] + velocity) < maximum) or (
                back and (pos_line[0] + velocity) > minimum):
            self.__canvas.move(line, direction * velocity, 0)

    def get_bbox(self, item=None):
        if item is None:
            item = self.__image_on_canvas
        return self.__canvas.bbox(item)
