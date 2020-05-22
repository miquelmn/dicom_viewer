# -*- coding: utf-8 -*-
""" Set of function to segment objects.

"""

from typing import List, Tuple
import numpy as np
from skimage import segmentation


def build_marker(markers: List[Tuple[int, int]], radius: int, img_size: Tuple[int, int, int]):
    """ Build marker image from a set of points.

    Args:
        markers:
        radius:
        img_size:

    Returns:

    """
    markers_img = np.zeros(img_size, dtype=np.int32)

    for idx, m in enumerate(markers):
        markers_img[max(0, m[0] - radius): min(m[0] + radius, img_size[0]),
                    max(0, m[1] - radius): min(m[1] + radius, img_size[1]),
                    max(0, m[2] - radius): min(m[2] + radius, img_size[2])] = idx + 1

    return markers_img


def apply_watershed(markers: np.ndarray, image: np.ndarray) -> np.ndarray:
    """ Applies watershed with markers.

    Args:
        markers:
        image:

    Returns:

    """
    mask = segmentation.watershed(image, markers)

    return mask
