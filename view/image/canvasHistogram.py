from view import view_component
import numpy as np
import tkinter as tk
import functions as funcs


class CanvasHistogram(view_component.VComponent):

    def __init__(self, parent, **kwargs):
        self.__parent = parent

        self.__canvas = None  # Tk.Canvas
        self.__image_on_canvas = None  # Canvas.Create_image
        self.__image_raw = None  # Numpy Array
        self.__image = None  # Tk image

        self.__min_line = None
        self.__max_line = None

        self.__size_img = [1000, 600]

        super().__init__(**kwargs)

    def set_function(self, **kwargs):
        pass

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
            img_raw = np.ones((500, 500)) * 255
        img = CanvasHistogram.numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, width=self.__size_img[0], height=self.__size_img[1])
        canvas.grid(row=self.row, column=self.column, sticky="nsew")
        image_on_canvas = canvas.create_image(20, 100, anchor="nw", image=img)

        self.__image_raw = img_raw
        self.__image = img
        self.__image_on_canvas = image_on_canvas
        self.__canvas = canvas

        self.__create_lines()

    def __create_lines(self):
        assert self.__canvas is not None

        canvas = self.__canvas
        bbox = canvas.bbox(self.__image_on_canvas)

        min_line = canvas.create_line(20, bbox[1] + 5, 20, bbox[3])
        max_line = canvas.create_line(bbox[2], bbox[1], bbox[2], bbox[3] - 1)

        self.__min_line = min_line
        self.__max_line = max_line

    def show_image(self, img_raw: np.ndarray):
        assert self.__image_on_canvas is not None

        histogram = funcs.get_histogram(img_raw)

        return self.show_histogram(histogram)

    def show_histogram(self, histogram: np.ndarray):
        assert self.__image_on_canvas is not None

        img = CanvasHistogram.numpy_2_tkinter(histogram)
        self.__canvas.itemconfig(self.__image_on_canvas, image=img)

        self.__image_raw = histogram
        self.__image = img

    def lines_bb(self):
        """
        Yield the bounding box of each line.

        The bounding box is defined by four integers. The couples indicated the top-left point and
        the bottom-right point.

        Returns:

        """
        for i in range(0, 2):
            yield self.__get_line(i)

    def move_line(self, id_line: int, front: bool, velocity: int):
        """
        Move the line indicated from the parameter.

        Args:
            id_line (int): If 0 the line moved is the minimum if it's 1 moves the max line
            front (bool): If true the line moves to the right else moves to the left.
            velocity (int): Speed of the movement

        Returns:

        """
        line = self.__get_line(id_line)

        direction = 1
        if front:
            direction = direction * -1

        self.__canvas.move(line, direction * velocity, 0)
