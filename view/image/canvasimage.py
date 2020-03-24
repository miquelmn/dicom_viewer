from view import view_component
import numpy as np
import tkinter as tk


class CanvasImage(view_component.VComponent):

    def __init__(self, parent, **kwargs):
        self.__canvas = None
        self.__image_on_canvas = None
        self.__parent = parent
        self.__image = None
        self.__scale_depth = None

        # Functions
        self.__f_depth = None
        self.__f_zoom = None
        self.__f_movements = None

        super().__init__(**kwargs)

    def set_function(self, movements_function):
        self.__f_movements = movements_function

    def draw(self):
        self.__draw_img()

    def __draw_img(self, img_raw=None):
        if img_raw is None:
            img_raw = np.ones((500, 500)) * 255
        img = CanvasImage.numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, width=600, height=300)
        canvas.bind("<Button-1>", self.__f_movements[0])
        canvas.bind("<ButtonRelease-1>", self.__f_movements[1])
        canvas.grid(row=self.row, column=self.column, sticky="nsew")
        image_on_canvas = canvas.create_image(20, 20, anchor="nw", image=img)



        # self.__scale_depth = scale_depth
        self.__image_raw = img_raw
        self.__image = img
        self.__image_on_canvas = image_on_canvas
        self.__canvas = canvas

    coord = None

    def show_image(self, img_raw: np.ndarray):
        assert self.__image_on_canvas is not None

        img = CanvasImage.numpy_2_tkinter(img_raw)
        self.__canvas.itemconfig(self.__image_on_canvas, image=img)

        self.__image = img

    def get_image_depth(self) -> int:
        return int(self.__scale_depth.get())
