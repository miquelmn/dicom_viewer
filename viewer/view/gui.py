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
    third = 2


DEFAULT_STATUS_BAR = "A l'espera de noves instruccions"


class View(tk.Tk):

    def __init__(self, title):
        super().__init__()

        self.__title = title
        self.__image_first = imageContainer.ContainerImage(self, histogram=True, relief=tk.RAISED,
                                                           bd=2)
        self.__image_second = imageContainer.ContainerImage(self, histogram=False, depth=False,
                                                            zoom=False, relief=tk.RAISED, bd=2)
        self.__image_merge = imageContainer.ContainerImage(self, histogram=False, depth=False,
                                                           zoom=False, relief=tk.RAISED,
                                                           bd=2)
        self.__button_functions = {}
        self.__func_selectors = []
        self.__status_bar = tk.Label(self, text=DEFAULT_STATUS_BAR, relief=tk.SUNKEN, bd=2,
                                     justify=tk.LEFT, anchor=tk.W)

        self.__fn_registration = None
        self.__fr_button = None
        self.__fr_images = None
        self.__registration_fields = {}

        self.__alpha = None
        self.__fn_alpha = None

    def set_functions(self, movements, depth, zoom, histogram, histogram_release, pixel_value,
                      distance, sel_dim, register, alpha, **kwargs):
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
            register:
            **kwargs:

        Returns:

        """
        self.__image_first.set_functions(movements, depth, zoom, histogram, histogram_release,
                                         pixel_value, distance)
        self.__func_selectors = [sel_dim]
        self.__button_functions = kwargs
        self.__fn_registration = register
        self.__fn_alpha = alpha

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

        self.__image_merge.draw()
        self.__image_merge.grid(row=0, column=3, columnspan=1, sticky="nswe")

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

        row = 0
        for row, b in enumerate(buttons):
            b.grid(row=row, column=0, sticky="ew", padx=5, columnspan=2)

        for values, func in self.__func_selectors:
            row += 1
            variable = tk.StringVar(fr_buttons)
            variable.set("First")  # default value

            tk.Label(fr_buttons, text="Dimensió", justify=tk.LEFT, anchor=tk.W).grid(row=row,
                                                                                     column=0,
                                                                                     sticky="nswe")
            tk.OptionMenu(fr_buttons, variable, *values, command=func).grid(row=row, column=1,
                                                                            sticky="ew", padx=5)

        row = self.__registration_menu(fr_buttons, first_row=row)
        row += 1
        tk.Label(fr_buttons, text="Fusió alpha", justify=tk.LEFT, anchor=tk.W,
                 font='Helvetica 11 bold').grid(row=row, column=0, sticky="nswe", pady=(15, 0))

        row += 1
        ttk.Separator(fr_buttons, orient="horizontal").grid(row=row, column=0, sticky="nswe",
                                                            pady=5, columnspan=2)

        row += 1
        tk.Label(fr_buttons, text="Alpha", justify=tk.LEFT, anchor=tk.W).grid(row=row, column=0,
                                                                              sticky="nswe",
                                                                              padx=5)
        self.__alpha = tk.Scale(fr_buttons, from_=0, to=100, orient=tk.HORIZONTAL).grid(row=row,
                                                                                        column=1,
                                                                                        sticky="nswe",
                                                                                        padx=5)
        row += 1
        tk.Button(fr_buttons, text="Fusió", command=self.__fn_alpha).grid(row=row, column=0,
                                                                          sticky="ew", padx=5,
                                                                          columnspan=2)

        fr_buttons.grid(row=0, column=0, sticky="ns")

        self.__fr_button = fr_buttons

    def __registration_menu(self, master, first_row: int):
        """ Draws the submenu for registration.

        Args:
            master:
            first_row:

        Returns:

        """
        row = first_row + 1

        tl = tk.Label(master, text="Registration", justify=tk.LEFT, anchor=tk.W,
                      font='Helvetica 11 bold')
        tl.grid(row=row, column=0, sticky="nswe", pady=(15, 0))

        row += 1
        ttk.Separator(master, orient="horizontal").grid(row=row, column=0, sticky="nswe", pady=5,
                                                        columnspan=2)

        fields = {"Learning rate": None, "Iterations": None}

        for field in fields.keys():
            row += 1

            tk.Label(master, text=field, justify=tk.LEFT, anchor=tk.W).grid(row=row,
                                                                            sticky="nswe")
            fields[field] = tk.Entry(master)
            fields[field].grid(row=row, column=1)

        options = {"Similarity": ["MSE", "Correlation", "Histogram"],
                   "Optimizer": ["Gradient descent", "LBFGS"],
                   "Interpolation": ["Linear", "B Spline", "Afí"]}

        for key, options_list in options.items():
            row += 1
            label = tk.Label(master, text=key, justify=tk.LEFT, anchor=tk.W)
            label.grid(row=row, column=0, sticky="nswe", pady=10)

            variable = tk.StringVar(master)
            variable.set(options_list[0])

            opt = tk.OptionMenu(master, variable, *options_list)
            opt.grid(row=row, column=1, sticky="nswe", columnspan=1, pady=5)
            options[key] = variable

        row = row + 1
        aux = tk.Button(master, text="Fer corregistre", command=self.__fn_registration)
        aux.grid(row=row, column=0, sticky="nswe", columnspan=2, pady=15)

        self.__registration_fields = {"Fields": fields, "Options": options}

        return row

    @property
    def registration_fields(self):
        """ Returns the field with the option for the registration.

        Returns:

        """
        reg_fields = self.__registration_fields

        res = {}
        for value in reg_fields.values():
            for sub_key, sub_value in value.items():
                aux = sub_value.get()
                res[sub_key] = aux

        return res

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
        elif img_container is ImageContID.third:
            self.__image_merge.update_image(img)
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

    @property
    def alpha(self):
        """ Returns the alpha of the selector.

        Returns:

        """
        alpha = 0
        if self.__alpha is not None:
            alpha = float(self.__alpha.get()) / 100

        return alpha
