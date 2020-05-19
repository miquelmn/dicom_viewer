# -*- coding: utf-8 -*-

import abc
from PIL import Image, ImageTk
import numpy as np
from typing import Tuple


class VComponent(abc.ABC):

    def __init__(self, row: int, column: int, size: Tuple[int, int]):
        self._functions = {}
        self._row = row
        self._column = column
        self._width = size[0]
        self._height = size[1]

    @abc.abstractmethod
    def draw(self):
        pass

    def set_function(self, functions: dict, **kwargs):
        self._functions = functions

    @staticmethod
    def numpy_2_tkinter(img_raw: np.ndarray):
        img = ImageTk.PhotoImage(image=Image.fromarray(img_raw))

        return img
