import numpy as np
from viewer.model import texture_features


def test_apply_filter():
    img = np.zeros((100, 100))
    kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])

    res = texture_features.apply_filter(img, kernel)

    assert img.shape[0] == res.shape[0] and img.shape[1] == res.shape[
        1], "Convolution with same padding"
    assert np.count_nonzero(res) == 0, "Expected results"
