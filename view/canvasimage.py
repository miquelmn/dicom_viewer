from view import view_component
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk


class CanvasImage(view_component.VComponent):

    def __init__(self, parent):
        self.__canvas = None
        self.__image_on_canvas = None
        self.__parent = parent
        self.__image = None
        self.__scale = None
        self.__n_images = 1

        super().__init__()

    def set_n_images(self, value: int):
        self.__n_images = value
        if self.__scale is not None:
            self.__scale.configure(to=value)

    def draw(self):
        self.__draw_img()

    def __draw_img(self, img_raw=None):
        if img_raw is None:
            img_raw = np.ones((500, 500)) * 255
        img = CanvasImage.__numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, width=300, height=300)
        canvas.grid(row=0, column=1, sticky="nsew")
        image_on_canvas = canvas.create_image(20, 20, anchor="nw", image=img)

        scale = tk.Scale(self.__parent, from_=0, to=self.__n_images, orient=tk.HORIZONTAL,
                         command=self.functions[0])
        scale.grid(row=1, column=1, sticky="nsew")

        self.__scale = scale
        self.__image_raw = img_raw
        self.__image = img
        self.__image_on_canvas = image_on_canvas
        self.__canvas = canvas

    def show_image(self, img_raw: np.ndarray):
        assert self.__image_on_canvas is not None

        img = CanvasImage.__numpy_2_tkinter(img_raw)
        self.__canvas.itemconfig(self.__image_on_canvas, image=img)

        self.__image = img

    def get_image_depth(self) -> int:
        return int(self.__scale.get())

    @staticmethod
    def __numpy_2_tkinter(img_raw: np.ndarray):
        img = ImageTk.PhotoImage(image=Image.fromarray(img_raw))

        return img
