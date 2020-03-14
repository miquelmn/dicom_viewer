from typing import List
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


class View(tk.Tk):

    def __init__(self, data: List[np.ndarray], title):
        self.__data = data
        self.__title = title
        self.__canvas = None
        self.__image_on_canvas = None
        self.__functions = None

        super().__init__()

    def set_functions(self, *args):
        self.__functions = args

    def set_title(self, titol: str):
        self.__title = titol


    @property
    def data(self) -> List[np.ndarray]:
        return self.__data

    @data.setter
    def data(self, val: List[np.ndarray]):
        self.__data = val

    @property
    def canvas(self) -> tk.Canvas:
        return self.__canvas

    def draw(self):
        """ Draws the GUI.

        Returns:

        """
        self.title(self.__title)
        self.rowconfigure(0, minsize=800, weight=1)
        self.columnconfigure(1, minsize=800, weight=1)

        self.__button_bar()
        self.__draw_img()

        self.mainloop()

    def __button_bar(self):
        fr_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)

        functions = self.__functions
        btn_open = tk.Button(fr_buttons, text="Obrir", command=functions[0])
        btn_save = tk.Button(fr_buttons, text="Save As...", command=functions[1])

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_save.grid(row=1, column=0, sticky="ew", padx=5)

        fr_buttons.grid(row=0, column=0, sticky="ns")

    def __draw_img(self, img_raw=None):
        if img_raw is None:
            img_raw = np.ones((100, 100)) * 150
        img = View.__numpy_2_tkinter(img_raw)

        canvas = tk.Canvas(self, width=300, height=300)
        canvas.grid(row=0, column=1, sticky="nsew")

        self.__image_on_canvas = canvas.create_image(20, 20, anchor="nw", image=img)
        self.__canvas = canvas

    def show_image(self, img_raw: np.ndarray):
        assert self.__image_on_canvas is not None

        img = View.__numpy_2_tkinter(img_raw)
        self.canvas.itemconfig(self.__image_on_canvas, image=img)

    @staticmethod
    def __numpy_2_tkinter(img_raw: np.ndarray):
        img = ImageTk.PhotoImage(image=Image.fromarray(img_raw))

        return img
