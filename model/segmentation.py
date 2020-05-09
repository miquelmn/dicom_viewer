# -*- coding: utf-8 -*-
""" Set of function to segment objects

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
    markers_img = np.ones(img_size)

    for idx, m in enumerate(markers):
        markers_img[m[0] - radius: m[0] + radius, m[1] - radius: m[1] + radius] = idx + 2

    return markers_img
