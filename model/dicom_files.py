from typing import List
from pydicom.filereader import dcmread
import numpy as np
import cv2


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

    @property
    def images(self) -> np.ndarray:
        """ Returns the images of the Dicom fIle

        Returns:

        """
        return self.__dicom_file.pixel_array

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        if self.__idx <= len(self):
            result = self.__dicom_file.pixel_array[:, :, self.__idx]
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
        if self.__zoom_factor > 1:
            original_size = np.array(img.shape)
            new_size = original_size * self.__zoom_factor

            img_resized = cv2.resize(img, tuple(new_size[::-1]))
            position = self.__position

            position[0] = max(position[0], 0)
            position[1] = max(position[1], 0)

            img = img_resized[position[0]:original_size[0] + position[0],
                              position[1]:original_size[1] + position[1]]

        return img

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
