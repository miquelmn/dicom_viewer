from view import gui, tktable
from tkinter.filedialog import askopenfilename
from model.dicom_files import DicomImage
from tkinter import messagebox


class Controller:

    def __init__(self, view: gui.View):
        self.__view = view
        self.__model = None

        self.__view.set_functions([self.open_file, self.show_headers, self.change_depth])

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

    def exist_model(self, func):
        def wrapper():
            if self.__model is None:
                messagebox.showerror("Error", "No has carregat una imatge vàlida")
            else:
                func()

        return wrapper

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
        depth = int(value)

        if self.__model is not None and depth < len(self.__model):
            self.__view.image.show_image(self.__model[depth])

    @exist_model
    def change_zoom(self, value):
        zoom = int(value)

        self.__model.resize_factor = zoom

    def start(self):
        self.__view.draw()
