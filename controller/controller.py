from view import gui
from tkinter.filedialog import askopenfilename
from model.dicom_files import DicomImage


class Controller:

    def __init__(self, view: gui.View):
        self.__view = view
        self.__model = None

        self.__view.set_functions([self.open_file])

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Dicom files", "*.dcm")]
        )
        if filepath:
            self.__model = DicomImage(filepath)
            self.__view.show_image(self.__model[0])
        self.__view.title(f"Simple Text Editor - {filepath}")
