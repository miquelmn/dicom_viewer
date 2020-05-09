import pytest
from model import segmentation
import numpy as np


def test_build_marker():
    marker_img = segmentation.build_marker([(50, 50)], radius=2, img_size=(100, 100))
    marker_area = (marker_img == 2).astype(np.uint8)

    marker_area = np.count_nonzero(marker_area)

    assert marker_area == (2 * 2)
