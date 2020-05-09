# -*- coding: utf-8 -*-
""" Set of function to segment objects.

"""

from typing import List, Tuple
import cv2
import numpy as np


def build_marker(markers: List[Tuple[int, int]], radius: int, img_size: Tuple[int, int]):
    """ Build marker image from a set of points.

    Args:
        markers:
        radius:
        img_size:

    Returns:

    """
    markers_img = np.zeros(img_size, dtype=np.int32)

    for idx, m in enumerate(markers):
        markers_img[m[0] - radius: m[0] + radius, m[1] - radius: m[1] + radius] = idx + 1

    return markers_img


def apply_watershed(markers: np.ndarray, image: np.ndarray) -> np.ndarray:
    """ Applies watershed with markers.

    Args:
        markers:
        image:

    Returns:

    """
    if len(markers.shape) != 2:
        raise Exception(
            "Watershed markers should be a 1D image get (" + str(markers.shape) + ") size")

    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    mask = cv2.watershed(image, markers)

    return mask
