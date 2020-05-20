# -*- coding: utf-8 -*-
""" Model class of an architecture MVC.

This model contains the information of each the images to visualize. The main focus of this class
is a set of transformations to the data.

TODO:
    Instead of showing through matplotlib save it to a variable.
"""

import random
import glob
import os
from typing import List, Union, Tuple
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pydicom.filereader import dcmread
from . import segmentation, texture_features

Num = Union[int, float]


def img_2_histogram(img: np.ndarray, size: Tuple[int, int], dpi: int = 96):
    """ Extract histogram from an image.

    Args:
        img:
        size:
        dpi:

    Returns:

    """
    width, height = size
    fig = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.axis('off')
    fig.tight_layout(pad=0)

    ax.hist(img.ravel())
    canvas.draw()

    histogram = np.fromstring(canvas.tostring_rgb(), dtype='uint8')

    histogram = histogram.reshape((height, width, -1))

    return histogram


class DicomFolder:
    """ Class to wrap a folder of images.

    """

    def __init__(self, path: str):
        self.__headers = {}
        self.__tensor = np.zeros((0, 0))

        self.__load_folder(path)

    def __load_folder(self, path: str):
        """ Load a dicom folder into the object.

        A folder of dicom files is a set of files dicom in a directory. This files are, in the
        correct order a depth image. Each of these files should share the same headers.

        Args:
            path (str):

        Returns:

        """
        files = glob.glob(os.path.join(path, "*.dcm"))
        files = sorted(files, key=lambda x: int(x.split(os.path.sep)[-1].split(".")[0]),
                       reverse=False)
        tensor = []

        img = {}
        for filename in files:
            img = dcmread(filename)
            tensor.append(img.pixel_array)

        if tensor:
            tensor = np.dstack(tensor)
            headers = img

        self.__headers = headers
        self.__tensor = tensor

    @property
    def pixel_array(self) -> np.ndarray:
        """ Returns the tensor that defines the 3D image.

        Returns:

        """
        return self.__tensor

    def items(self):
        """ Analog to a dictionary function.

        Wraps the headers function

        Returns:

        """
        return self.__headers.items()


class DicomImage:
    """
    Wrapper class for the pydicom library.

    The DicomImage is an iterable object though the different 3D channels

    """

    def __init__(self, path: str, max_size: List[Num] = None):
        self.__path = path
        if os.path.isdir(path):
            self.__dicom_file = DicomFolder(path)
        else:
            self.__dicom_file = dcmread(path)
        self.__zoom_factor = 1
        self.__position = [0, 0]

        self.__contrast = [0, 1]

        if max_size is None:
            max_size = [float('inf'), float('inf')]
        self.__max_size = max_size
        self.__real_size = None
        self.__reduced_size = None
        self.__selected_dim = 0

    def apply_watershed(self, item, markers: List[Tuple[int, int]]) -> np.ndarray:
        """ Applies watershed algorithm with markers.


        Args:
            item:
            markers:

        Returns:

        """
        img = self[item]

        img = ((img - img.min()) / (img.max() - img.min())) * 255
        img = img.astype(np.uint8)

        markers = segmentation.build_marker(markers, radius=10, img_size=img.shape)
        mask = segmentation.apply_watershed(markers, img)

        return mask

    def get_texture_features(self, regions: np.ndarray, item: int):
        """ Gets texture features of the image item.

        Args:
            regions:
            item:

        Returns:

        """
        img = self[item]
        kernels = texture_features.create_filter_bank()
        kernels = random.sample(kernels, k=1)
        res = texture_features.apply_filters_region_img(regions, img, kernels)

        for r, textures in res.items():
            plt.figure()
            plt.title("Regions " + str(r))
            plt.imshow(textures[0])
        plt.show()

    @property
    def images(self) -> np.ndarray:
        """ Returns the images of the Dicom fIle

        Returns:

        """
        return self.__dicom_file.pixel_array

    @property
    def dim(self) -> Num:
        return self.__selected_dim

    @dim.setter
    def dim(self, value: int):
        """ Selects which dimension to return.

        Args:
            value (int): Integer of the dimension.

        Returns:

        """
        self.__reduced_size = None
        self.__selected_dim = value

    def set_max_size(self, size):
        self.__max_size = size

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
        return self.images.shape[self.__selected_dim]

    def __getitem__(self, item):
        """ Magic method to use the class with the interface [item].

        Args:
            item:

        Returns:

        """

        return self.get_img(item, dim=self.__selected_dim)

    def get_img(self, item, flag_contrast: bool = True, flag_zoom: bool = True,
                dim: int = 0):
        """ Get the cut of the image passed as parameter

        Args:
            item:
            flag_contrast:
            flag_zoom:
            dim:

        Returns:

        """
        img = self.__get_raw_image(item, dim)

        size = None
        if self.__real_size is None:
            self.__real_size = img.shape[::-1]

        if self.__reduced_size is None:
            if img.shape[0] > self.__max_size[0] or img.shape[1] > self.__max_size[1]:
                max_idx = np.argmax(img.shape)
                min_idx = np.argmin(img.shape)

                if max_idx == min_idx:
                    min_idx = (min_idx + 1) % len(img.shape)

                rel = img.shape[min_idx] / img.shape[max_idx]

                max_val = self.__max_size[max_idx]
                min_val = int(rel * max_val)

                size = np.zeros(2, dtype=int)

                size[max_idx] = max_val
                size[min_idx] = min_val

                size = tuple(size)
                self.__reduced_size = size
        else:
            size = self.__reduced_size

        if size is not None:
            img = cv2.resize(img, size)

        if flag_contrast:
            img = DicomImage.__set_contrast(img, self.__contrast)
        if flag_zoom and self.__zoom_factor > 1:
            img = DicomImage.__set_zoom(img, self.__zoom_factor, self.position)

        return img

    def get_histogram(self, item: int):
        """ Get the histogram of the cut in the depth passed as parameter.

        Args:
            item:

        Returns:

        """
        img = self.__get_raw_image(item)

        return img_2_histogram(img, size=self.__max_size)

    def get_distance(self, point_1, point_2) -> float:
        """ Calculate the distance between two points.

        Args:
            point_1 (np.array):
            point_2 (np.array):

        Returns:
            A float containing the distance between two points on the image
        """
        point_1 = point_1 / self.__zoom_factor
        point_2 = point_2 / self.__zoom_factor

        if self.__reduced_size is not None:
            rel = self.__real_size[0] / self.__reduced_size[0], self.__real_size[1] / \
                  self.__reduced_size[1]
            point_1 = np.multiply(point_1, rel)
            point_2 = np.multiply(point_2, rel)

        distance = np.linalg.norm(point_1 - point_2)

        return distance

    def get_voxel(self, x, y, z):
        """ Get the value of the voxel (x,y,z)

        Args:
            x:
            y:
            z:

        Returns:

        """
        img = self.get_img(z, flag_contrast=False, flag_zoom=True, dim=self.__selected_dim)

        return img[y][x]

    def __get_raw_image(self, item, dim=None):
        if dim is None:
            dim = self.dim
        return self.__dicom_file.pixel_array.take(indices=item, axis=dim)

    @staticmethod
    def __set_zoom(img: np.ndarray, zoom: Num, position: List[int]):
        """ Renders and image with zoom and it's position

        This function apply zoom to an image. The zoom is aplied resources two steps. Fist of all the
        image is resized to the size passed as parameter. Secondly the resized image is cropped
        to the original size. Doing this we accomplish a zoom effect. To move the zoom position
        we add a the value to the initial crop position.

        Args:
            img (np.ndarray): Image to make the zoom
            zoom (Number):
            position:

        Returns:

        """
        if zoom < 1:
            raise Exception("Zoom to be applied should be higher or equal than 1")

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
        """ Change the contrast of the image.

        The contrast of an image can be set through a numerical transformation.

        Args:
            img:
            contrast:

        Returns:

        """
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

        img_c[img >= maximum_value] = 1
        img_c[img <= minimum_value] = 0

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

    def corregister(self, input_img):
        pass
