from view import view_component
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from typing import List


class CanvasImage(view_component.VComponent):

    def __init__(self, parent):
        self.__canvas = None
        self.__image_on_canvas = None
        self.__parent = parent
        self.__image = None
        self.__scale_depth = None
        self.__n_images = 1

        # Functions
        self.__f_depth = None
        self.__f_zoom = None
        self.__f_movements = None

        super().__init__()

    def set_function(self, depth_function, zoom_function, movements_function):
        self.__f_depth = depth_function
        self.__f_zoom = zoom_function
        self.__f_movements = movements_function

    def set_n_images(self, value: int):
        self.__n_images = value
        if self.__scale_depth is not None:
            self.__scale_depth.configure(to=value)

    def draw(self):
        self.__draw_img()

    def __draw_img(self, img_raw=None):
        if img_raw is None:
            img_raw = np.ones((500, 500)) * 255
        img = CanvasImage.__numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, width=300, height=300)
        canvas.bind("<Button-1>", self.__f_movements[0])
        canvas.bind("<ButtonRelease-1>", self.__f_movements[1])
        canvas.grid(row=0, column=1, sticky="nsew")
        image_on_canvas = canvas.create_image(20, 20, anchor="nw", image=img)

        scale_depth = tk.Scale(self.__parent, from_=0, to=self.__n_images, orient=tk.HORIZONTAL,
                               command=self.__f_depth)
        scale_depth.grid(row=1, column=1, sticky="nsew")

        scale_zoom = tk.Scale(self.__parent, from_=1, to=100, command=self.__f_zoom)
        scale_zoom.grid(row=0, column=2, sticky="nsew")

        self.__scale_depth = scale_depth
        self.__image_raw = img_raw
        self.__image = img
        self.__image_on_canvas = image_on_canvas
        self.__canvas = canvas

    coord = None

    def reset_t(self, event):
        print(self.coord)
        print(event.x, event.y)

    def prova(self, event):
        self.coord = event.x, event.y

    def show_image(self, img_raw: np.ndarray):
        assert self.__image_on_canvas is not None

        img = CanvasImage.__numpy_2_tkinter(img_raw)
        self.__canvas.itemconfig(self.__image_on_canvas, image=img)

        self.__image = img

    def get_image_depth(self) -> int:
        return int(self.__scale_depth.get())

    @staticmethod
    def __numpy_2_tkinter(img_raw: np.ndarray):
        img = ImageTk.PhotoImage(image=Image.fromarray(img_raw))

        return img
