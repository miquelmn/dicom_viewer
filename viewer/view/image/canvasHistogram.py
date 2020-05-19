""" Graphical component to show the histogram in the GUI.

An histogram is a representation discrete representation of an image.

"""
from viewer.view.image import canvasimage
import numpy as np


class CanvasHistogram(canvasimage.CanvasImage):

    def __init__(self, **kwargs):
        self.__min_line = None
        self.__max_line = None

        super().__init__(**kwargs)

    def draw(self):
        super().draw()
        self.__create_lines()

    def __get_line(self, idx):
        if idx != 0 and idx != 1:
            raise Exception("Index out of bounds")

        if idx == 0:
            return self.__min_line
        elif idx == 1:
            return self.__max_line

    def __create_lines(self):
        assert self._canvas is not None

        canvas = self._canvas
        bbox = canvas.bbox(self._image_on_canvas)

        max_line = canvas.create_line(bbox[2] - 10, bbox[1], bbox[2] - 10, bbox[3])
        min_line = canvas.create_line(bbox[0], bbox[1], bbox[0], bbox[3])

        self.__max_line = max_line
        self.__min_line = min_line

    def _reset_local_gui(self):
        self.reset_lines()

    def reset_lines(self):
        """ Reset control lines to the initial position.

        Returns:

        """
        bbox = np.array(self._canvas.bbox(self._image_on_canvas))

        self._canvas.coords(self.__max_line, bbox[2] - 10, bbox[1], bbox[2] - 10, bbox[3] - 1)
        self._canvas.coords(self.__min_line, bbox[0], bbox[1], bbox[0], bbox[3] - 1)

    def lines_bb(self):
        """
        Yield the bounding box of each line.

        The bounding box is defined by four integers. The couples indicated the top-left point and
        the bottom-right point.

        Returns:

        """
        for i in range(0, 2):
            line = self.__get_line(i)
            yield self._canvas.bbox(line)

    def move_line(self, id_line: int, back: bool, velocity: int):
        """
        Move the line indicated from the parameter.

        Args:
            id_line (int): If 0 the line moved is the minimum if it's 1 moves the max line
            back (bool): If true the line moves to the right else moves to the left.
            velocity (int): Speed of the movement

        Returns:

        """
        line = self.__get_line(id_line)
        bbox = self.get_bbox()
        maximum = bbox[2]
        minimum = bbox[0]
        pos_line = self.get_bbox(line)

        direction = 1
        if back:
            direction = direction * -1

        if ((not back) and (pos_line[0] + velocity) < maximum) or (
                back and (pos_line[0] + -1 * velocity) > minimum):
            self._canvas.move(line, direction * velocity, 0)
