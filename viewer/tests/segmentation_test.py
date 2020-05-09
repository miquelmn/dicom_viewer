from viewer.model import segmentation
import numpy as np
import cv2


def test_build_marker():
    radius = 5

    marker_img = segmentation.build_marker([(50, 50)], radius=radius, img_size=(100, 100))
    marker_area = (marker_img == 1).astype(np.uint8)

    marker_area = np.count_nonzero(marker_area)

    assert marker_area == ((radius * 2) * (radius * 2)), "Area of the marker"


def test_watershed():
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[25:75, 25:75] = 255

    marker_img = segmentation.build_marker([(50, 50)], radius=5, img_size=(100, 100))

    segmented = segmentation.apply_watershed(marker_img, mask)

    assert len(mask.shape) == len(segmented.shape), "Good dimensions"
    assert mask.shape[0] == segmented.shape[0] and mask.shape[1] == segmented.shape[1], "Good shape"
    assert np.allclose(segmented, mask), "Good segmentation"
