import abc
from PIL import Image, ImageTk
import numpy as np


class VComponent(abc.ABC):

    def __init__(self, row: int, column: int):
        self.functions = None
        self.row = row
        self.column = column

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def set_function(self, **kwargs):
        pass

    @staticmethod
    def numpy_2_tkinter(img_raw: np.ndarray):
        img = ImageTk.PhotoImage(image=Image.fromarray(img_raw))

        return img
