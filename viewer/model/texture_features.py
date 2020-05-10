# -*- coding: utf-8 -*-
""" Module to extract textures features.

This module allow to extract texture features from regions of the image. A texture feature is
defined by a set of kernels. To get the texture features an image is convolved with these kernels.

"""

from typing import List
import numpy as np
from scipy import ndimage
from skimage import filters


def create_filter_bank():
    """ Create a bank of filters

    Adapted from scikit-image doc.

    Returns:

    """
    kernels = []
    for theta in range(6):
        theta = theta / 4. * np.pi
        for sigma in (1, 3, 5):
            for frequency in (0.05, 0.15, 0.25):
                kernel = np.real(
                    filters.gabor_kernel(frequency, theta=theta, sigma_x=sigma, sigma_y=sigma))
                kernels.append(kernel)
    return kernels


def apply_filter(image, kernel):
    """ Applies a filter to an image

    Convolve an image with the filter passed as parameter.

    Args:
        image:
        kernel:

    Returns:

    """
    return ndimage.convolve(image, kernel, mode='reflect')


def apply_filters_region_img(regions: np.ndarray, img: np.ndarray, bank_kernels: List[np.ndarray]):
    """ Applies bank of filters to regions of an image.

    The regions of the image are defined in the first parameter. The pixels of each region have the
    same value. These values are in a from 1 to the max value of the region. The values less than 1
    are discarded.

    Args:
        regions:
        img:
        bank_kernels:
    Returns:

    """

    res = {}
    for region_value in range(1, regions.max()):
        region = np.copy(img)
        region[regions != region_value] = 0

        row = []
        for kernel in bank_kernels:
            row.append(apply_filter(region, kernel))
        res[region_value] = row

    return res
