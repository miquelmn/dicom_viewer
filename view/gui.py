from typing import List
import tkinter as tk
import numpy as np
from . import canvasimage


class View(tk.Tk):

    def __init__(self, data: List[np.ndarray], title):
        self.__data = data
        self.__title = title
        self.__canvas_image = None
        self.__functions = None

        super().__init__()

    def set_functions(self, **kwargs):
        self.__functions = kwargs

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

    @property
    def image(self) -> canvasimage.CanvasImage:
        return self.__canvas_image

    def draw(self):
        """ Draws the GUI.

        Returns:

        """
        self.title(self.__title)
        self.rowconfigure(0, minsize=800, weight=1)
        self.columnconfigure(1, minsize=800, weight=1)

        self.__button_bar()
        self.__canvas_image = canvasimage.CanvasImage(parent=self)

        self.image.set_function(depth_function=self.__functions["depth_c"],
                                zoom_function=self.__functions["zoom_c"],
                                movements_function=self.__functions["movement"])
        self.image.draw()

        self.mainloop()

    def __button_bar(self):
        fr_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)

        functions = self.__functions

        btn_open = tk.Button(fr_buttons, text="Obrir", command=functions["file_o"])
        btn_headers = tk.Button(fr_buttons, text="Capceleres", command=functions["header_s"])

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_headers.grid(row=1, column=0, sticky="ew", padx=5)

        fr_buttons.grid(row=0, column=0, sticky="ns")
