# -*- coding: utf-8 -*-
""" Class to generate the view of the app

The view of the apps is fully defined in this module. The view is made with the library tkinter

Classes:
    View (tkinter.Tk). Class containing the main window.
    ImageContId (enum). Enum to identify wich of the two imageContainer use.

"""

import tkinter as tk
from tkinter import ttk
from enum import Enum
import numpy as np
from viewer.view.image import imageContainer


class ImageContID(Enum):
    """ Interface to known wich container a function threads.

    """
    principal = 0
    secondary = 1


DEFAULT_STATUS_BAR = "A l'espera de noves instruccions"


class View(tk.Tk):

    def __init__(self, title):
        super().__init__()

        self.__title = title
        self.__image_first = imageContainer.ContainerImage(self, histogram=True, relief=tk.RAISED,
                                                           bd=2)
        self.__image_second = imageContainer.ContainerImage(self, histogram=False, relief=tk.RAISED,
                                                            bd=2)
        self.__button_functions = {}
        self.__func_selectors = []
        self.__status_bar = tk.Label(self, text=DEFAULT_STATUS_BAR, relief=tk.SUNKEN, bd=2,
                                     justify=tk.LEFT, anchor=tk.W)

        self.__fr_button = None
        self.__fr_images = None

    def set_functions(self, movements, depth, zoom, histogram, histogram_release, pixel_value,
                      distance, sel_dim, **kwargs):
        """ Set listeners for the events handled

        Args:
            movements:
            depth:
            zoom:
            histogram:
            histogram_release:
            pixel_value:
            distance:
            sel_dim:
            **kwargs:

        Returns:

        """
        self.__image_first.set_functions(movements, depth, zoom, histogram, histogram_release,
                                         pixel_value, distance)
        self.__func_selectors = [sel_dim]
        self.__button_functions = kwargs

    def set_title(self, titol: str):
        """ Set the window title.

        Args:
            titol:

        Returns:

        """
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

        self.__image_first.draw()
        self.__image_first.grid(row=0, column=1, columnspan=1, sticky="nswe")

        self.__image_second.draw()
        self.__image_second.grid(row=0, column=2, columnspan=1, sticky="nswe")

        self.__status_bar.grid(row=len(self.__func_selectors) + 1, column=0, columnspan=4,
                               sticky="nswe")

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

        buttons.append(ttk.Separator(fr_buttons, orient='horizontal'))

        for values, func in self.__func_selectors:
            variable = tk.StringVar(fr_buttons)
            variable.set("First")  # default value

            buttons.append(tk.OptionMenu(fr_buttons, variable, *values, command=func))

        for row, b in enumerate(buttons):
            b.grid(row=row, column=0, sticky="ew", padx=5)

        fr_buttons.grid(row=0, column=0, sticky="ns")

        self.__fr_button = fr_buttons

    def show_image(self, img, histogram: np.ndarray = None,
                   img_container: ImageContID = ImageContID.principal):
        """ Show a numpy array into the GUI.

        Args:
            img:
            histogram:
            img_container:

        Returns:

        """
        if img_container is ImageContID.secondary:
            self.__image_second.update_image(img)
        else:
            self.__image_first.update_image(img, histogram)

    def set_max_depth(self, max_depth: int, img_container: ImageContID = ImageContID.principal):
        """ Set max depth for the image containers.

        The image containers has the ability to move through multiples axis of 3D image. This
        function set the maximum value of this movement.

        Args:
            max_depth (int):
            img_container (ImageContID):
        """

        if img_container is ImageContID.secondary:
            image = self.__image_second
        else:
            image = self.__image_first

        image.set_n_images(max_depth)

    def set_text(self, text):
        """ Change label value of the secondary image.

        Args:
            text:

        Returns:

        """
        self.__image_second.set_text(text)

    def move_line(self, id_line: int, front: bool, velocity: int):
        self.__image_first.move_histogram_line(id_line, front, velocity)

    def lines_position(self):
        return self.__image_first.lines_position()

    def get_histogram_position(self):
        return self.__image_first.get_histogram_position()

    def get_image_position(self):
        return self.__image_first.get_image_position()

    def set_pixel_text(self, value: str):
        self.__image_first.set_text_value(value)

    def set_distance_text(self, value: str):
        self.__image_first.set_distance_value(value)

    @property
    def img_space(self):
        return self.__image_first.img_space

    @property
    def depth(self):
        if self.__image_second is None:
            return self.__image_first.depth
        else:
            return self.__image_first.depth, self.__image_second.depth

    def reset_status_bar(self):
        """ Resets the value of the update bar to the default one.

        Returns:

        """
        self.__status_bar['text'] = DEFAULT_STATUS_BAR

    def update_status_bar(self, status: str):
        """ Updates the status bar

        Args:
            status:

        Returns:

        """
        self.__status_bar['text'] = status
