from viewer.view import view_component
import numpy as np
import tkinter as tk


class CanvasImage(view_component.VComponent):

    def __init__(self, parent, **kwargs):
        self._canvas = None
        self._image_on_canvas = None
        self.__parent = parent
        self.__image = None
        self.__scale_depth = None
        self.__image_raw = None

        super().__init__(**kwargs)

    def draw(self):
        self.__draw_img()

    def __draw_img(self, img_raw=None):
        if img_raw is None:
            img_raw = np.ones((self._height, self._width)) * 255
        img = super().numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self.__parent, bd=0, width=self._width, height=self._height)
        canvas.grid(row=self._row, column=self._column, sticky="new")
        image_on_canvas = canvas.create_image(10, 0, anchor="nw", image=img)

        self.__image_raw = img_raw
        self.__image = img
        self._image_on_canvas = image_on_canvas
        self._canvas = canvas

        self.__bind_functions()

    def __bind_functions(self):
        canvas = self._canvas
        for k, func in self._functions.items():
            canvas.bind(k, func)

    def show_image(self, img_raw: np.ndarray):
        assert self._image_on_canvas is not None

        pre_bbox = np.array(self._canvas.bbox(self._image_on_canvas))
        pre_size = np.array([pre_bbox[2] - pre_bbox[0], pre_bbox[3] - pre_bbox[1]])

        img = CanvasImage.numpy_2_tkinter(img_raw)
        self._canvas.itemconfig(self._image_on_canvas, image=img)
        bbox = np.array(self._canvas.bbox(self._image_on_canvas))
        size = np.array([bbox[2] - bbox[0], bbox[3] - bbox[1]])

        if np.linalg.norm((pre_size - size)) > 10:
            self._reset_local_gui()

        self.__image_raw = img_raw
        self.__image = img

    def get_bbox(self, item=None):
        if item is None:
            item = self._image_on_canvas
        return self._canvas.bbox(item)

    def get_image_depth(self) -> int:
        return int(self.__scale_depth.get())

    def _reset_local_gui(self):
        pass
