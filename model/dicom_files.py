from typing import List, Union
from pydicom.filereader import dcmread
import numpy as np
import cv2

Num = Union[int, float]


class DicomImage:
    """
    Wrapper class for the pydicom library.

    The DicomImage is an iterable object though the different 3D channels

    """

    def __init__(self, path: str):
        self.__path = path
        self.__dicom_file = dcmread(path)
        self.__zoom_factor = 1
        self.__position = [0, 0]

        self.__contrast = [0, 1]

    @property
    def images(self) -> np.ndarray:
        """ Returns the images of the Dicom fIle

        Returns:

        """
        return self.__dicom_file.pixel_array

    def minimum_value(self, item: int) -> Num:
        return self.__get_raw_image(item).min()

    def maximum_value(self, item: int) -> Num:
        return self.__get_raw_image(item).max()

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        if self.__idx <= len(self):
            result = self[self.__idx]
            self.__idx += 1
            return result
        else:
            raise StopIteration

    @property
    def resize_factor(self):
        return self.__zoom_factor

    @resize_factor.setter
    def resize_factor(self, value):
        self.__zoom_factor = value

    @property
    def contrast(self):
        return self.__contrast

    @contrast.setter
    def contrast(self, value: List[int]):
        self.__contrast = value

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value: List[int]):
        self.__position = value

    def __len__(self):
        return self.images.shape[2]

    def __getitem__(self, item):
        """ Magic method to use the class with the interface [item].

        Args:
            item:

        Returns:

        """
        img = self.__dicom_file.pixel_array[:, :, item]
        img = DicomImage.__set_contrast(img, self.__contrast)
        if self.__zoom_factor > 1:
            img = DicomImage.__set_zoom(img, self.__zoom_factor, self.position)

        return img

    def __get_raw_image(self, item):
        return self.__dicom_file.pixel_array[:, :, item]

    @staticmethod
    def __set_zoom(img: np.ndarray, zoom: Num, position: List[int]):
        """ Renders and image with zoom and it's position

        This function apply zoom to an image. The zoom is aplied in two steps. Fist of all the
        image is resized to the size passed as parameter. Secondly the resized image is cropped
        to the original size. Doing this we accomplish a zoom effect. To move the zoom position
        we add a the value to the initial crop position.

        Args:
            img (np.ndarray): Image to make the zoom
            zoom (Number):
            position:

        Returns:

        """
        assert zoom > 1

        original_size = np.array(img.shape)
        new_size = original_size * zoom

        img_resized = cv2.resize(img, tuple(new_size[::-1]))
        position = position

        position[0] = max(position[0], 0)
        position[1] = max(position[1], 0)

        img = img_resized[position[0]:original_size[0] + position[0],
              position[1]:original_size[1] + position[1]]

        return img

    @staticmethod
    def __set_contrast(img: np.ndarray, contrast: List[Num]):
        assert max(contrast) <= 1 and min(contrast) >= 0

        img_c = np.copy(img)
        img_c = img_c.astype(np.float)

        adder = abs(int(min(0, img.min())))

        maximum_value = (img.max() + adder) * max(contrast)
        minimum_value = (img.max() + adder) * min(contrast)

        maximum_value -= adder
        minimum_value -= adder

        reverse_selection = ((img > minimum_value) & (img < maximum_value))
        img_c[reverse_selection] = (img_c[reverse_selection] - minimum_value) / (
                maximum_value - minimum_value)

        img_c[img > maximum_value] = 1
        img_c[img < minimum_value] = 0

        img_c = img_c * 255

        return img_c

    def get_header(self):
        """ Get a header element

        Iterate over the headers. Returns a tuple of the key and the values. It's a generator so
        it's an iterable. The best way to use this function is with a for.

        Returns:
            Tuple of key and value for every header.
        """
        for k, v in self.__dicom_file.items():
            try:
                yield k, v
            except AttributeError:
                pass

    def move_image(self, differential):
        self.position += differential[::-1] // 2
