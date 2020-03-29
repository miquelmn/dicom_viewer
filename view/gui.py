import tkinter as tk
import numpy as np
from view.image import imageContainer


class View(tk.Tk):

    def __init__(self, title):
        super().__init__()

        self.__title = title
        self.__image_container = imageContainer.ContainerImage(self, relief=tk.RAISED, bd=2)
        self.__functions = None

        self.__fr_button = None
        self.__fr_images = None

    def set_functions(self, movements, depth, zoom, histogram, histogram_release, pixel_value,
                      distance, **kwargs):
        self.__image_container.set_functions(movements, depth, zoom, histogram, histogram_release,
                                             pixel_value, distance)
        self.__functions = kwargs

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
        fr_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)

        functions = self.__functions

        btn_open = tk.Button(fr_buttons, text="Obrir", command=functions["file_o"])
        btn_headers = tk.Button(fr_buttons, text="Capceleres", command=functions["header_s"])
        btn_adv_viewer = tk.Button(fr_buttons, text="Visualitzador avançat",
                                   command=functions["adv_viewer"])
        btn_history = tk.Button(fr_buttons, text="Historial", command=functions["history"])

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_headers.grid(row=1, column=0, sticky="ew", padx=5)
        btn_adv_viewer.grid(row=2, column=0, sticky="ew", padx=5)
        btn_history.grid(row=3, column=0, sticky="ew", padx=5)

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
