from viewer.model import segmentation
import numpy as np
import cv2


def test_build_marker():
    """


    """
    marker_img = segmentation.build_marker([(50, 50)], radius=5, img_size=(100, 100))
    marker_area = (marker_img == 1).astype(np.uint8)

    marker_area = np.count_nonzero(marker_area)

    assert marker_area == (5 * 5)


def test_watershed():
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[25:75, 25:75] = 255

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    print(mask.shape)

    marker_img = segmentation.build_marker([(50, 50)], radius=5, img_size=(100, 100)).astype(
        np.int32)

    segmented = segmentation.apply_watershed(marker_img, mask)

    assert np.allclose(segmented, mask[:, :, 0])
