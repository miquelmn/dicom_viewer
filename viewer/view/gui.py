# -*- coding: utf-8 -*-
""" Class to generate the view of the app

The view of the apps is fully defined in this module. The view is made with the library tkinter

Class:
    View (tkinter.Tk). Class containing the main window.

"""

import tkinter as tk
import numpy as np
from viewer.view.image import imageContainer


class View(tk.Tk):

    def __init__(self, title):
        super().__init__()

        self.__title = title
        self.__image_container = imageContainer.ContainerImage(self, relief=tk.RAISED, bd=2)
        self.__button_functions = {}
        self.__func_selectors = []

        self.__fr_button = None
        self.__fr_images = None

    def set_functions(self, movements, depth, zoom, histogram, histogram_release, pixel_value,
                      distance, sel_dim, **kwargs):
        self.__image_container.set_functions(movements, depth, zoom, histogram, histogram_release,
                                             pixel_value, distance)
        self.__func_selectors = [sel_dim]
        self.__button_functions = kwargs

    def set_title(self, titol: str):
        self.__title = titol

    @property
    def canvas(self) -> tk.Canvas:
        return self.__canvas

    def draw(self):
        """ Draws the GUI.

        Returns:

        """
        self.title(self.__title)
        self.rowconfigure(0, minsize=800, weight=1)
        self.columnconfigure(2, minsize=50, weight=2)

        self.__button_bar()

        self.__image_container.draw()
        self.__image_container.grid(row=0, column=1, columnspan=3, sticky="nswe")

        self.mainloop()

    def __button_bar(self):
        """ Instance a button bar for the GUI.

        The GUI of this app is formed by two parts. The first one are a set of element of control.
        The main part show the image and the histogram. This function creates the control part.

        Returns:

        """
        fr_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)

        functions = self.__button_functions

        buttons = []
        for name, func in functions.items():
            name = name.replace("_", " ")
            buttons.append(tk.Button(fr_buttons, text=name, command=func))

        for values, func in self.__func_selectors:
            variable = tk.StringVar(fr_buttons)
            variable.set("First")  # default value

            buttons.append(tk.OptionMenu(fr_buttons, variable, *values, command=func))

        for row, b in enumerate(buttons):
            b.grid(row=row, column=0, sticky="ew", padx=5)

        fr_buttons.grid(row=0, column=0, sticky="ns")

        self.__fr_button = fr_buttons

    def show_image(self, img, histogram: np.ndarray = None):
        self.__image_container.update_image(img, histogram)

    def set_n_images(self, value: int):
        self.__image_container.set_n_images(value)

    def move_line(self, id_line: int, front: bool, velocity: int):
        self.__image_container.move_histogram_line(id_line, front, velocity)

    def lines_position(self):
        return self.__image_container.lines_position()

    def get_histogram_position(self):
        return self.__image_container.get_histogram_position()

    def get_image_position(self):
        return self.__image_container.get_image_position()

    def set_pixel_text(self, value: str):
        self.__image_container.set_text_value(value)

    def set_distance_text(self, value: str):
        self.__image_container.set_distance_value(value)

    @property
    def img_space(self):
        return self.__image_container.img_space
