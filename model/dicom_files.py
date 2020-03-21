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
        self.__images = dcmread(path)
        self.__zoom_factor = 1

    @property
    def images(self):
        return self.__images

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        if self.__idx <= len(self):
            result = self.__images.pixel_array[:, :, self.__idx]
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

    def __len__(self):
        return self.images.pixel_array.shape[2]

    def __getitem__(self, item):
        img = self.__images.pixel_array[:, :, item]
        if self.__zoom_factor > 1:
            original_size = np.array(img.shape)
            new_size = original_size * self.__zoom_factor

            img_resized = cv2.resize(img, tuple(new_size[::-1]))
            diffs = new_size - original_size
            img = img_resized[diffs[0] // 2:new_size[0] - diffs[0] // 2,
                              diffs[1] // 2:new_size[1] - diffs[1] // 2]

        return img

    def get_header(self):
        for k, v in self.__images.items():
            try:
                yield k, v
            except AttributeError:
                pass
