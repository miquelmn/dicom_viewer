from view import gui, tktable
from tkinter.filedialog import askopenfilename
from model.dicom_files import DicomImage
from tkinter import messagebox
import numpy as np


def exist_model(func):
    def wrapper(controller, *args):
        if controller.is_model():
            func(controller, *args)
        else:
            messagebox.showerror("Error", "No has carregat una imatge vàlida")

    return wrapper


class Controller:

    def __init__(self, view: gui.View):
        self.__view = view
        self.__model = None
        self.__depth = 0

        self.__position_first = None
        self.__view.set_functions(file_o=self.open_file, header_s=self.show_headers,
                                  depth_c=self.change_depth, zoom_c=self.change_zoom,
                                  movement=[self.initial_movement, self.movement])

    def is_model(self) -> bool:
        return self.__model is not None

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Dicom files", "*.dcm")]
        )
        if filepath:
            self.__model = DicomImage(filepath)
            self.__view.image.show_image(self.__model[0])
            self.__view.image.set_n_images(len(self.__model))
        self.__view.title(f"DICOM Reader - {filepath}")

    @exist_model
    def show_headers(self):
        dades = []

        for h, v in self.__model.get_header():
            str_v = str(v)
            str_h = str(h)
            if hasattr(v, 'length'):
                if v.length > 200:
                    print(v.length)
                    str_v = str_v[:400]
            dades.append([str_h, str_v])
        tktable.make_table("Capceleres", dades)

    @exist_model
    def change_depth(self, value):
        depth = int(value) // 2
        self.__depth = depth

        self.__update_view_image()

    @exist_model
    def change_zoom(self, value):
        zoom = int(value)

        self.__model.resize_factor = zoom
        self.__update_view_image()

    @exist_model
    def initial_movement(self, event):
        self.__position_first = np.array([event.x, event.y])

    @exist_model
    def movement(self, event):
        assert self.__position_first is not None

        position = np.array([event.x, event.y])
        old_position = self.__position_first

        self.__position_first = None

        self.__model.move_image(old_position - position)
        self.__update_view_image()

    def __update_view_image(self):
        depth = self.__depth

        if self.__model is not None and depth < len(self.__model):
            self.__view.image.show_image(self.__model[depth])

    def start(self):
        self.__view.draw()
