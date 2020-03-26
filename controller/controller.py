from view import gui, tktable
from tkinter.filedialog import askopenfilename
from model.dicom_files import DicomImage
from tkinter import messagebox
import numpy as np
import math
from matplotlib import pyplot as plt
from typing import List, Union


def exist_model(func):
    def wrapper(controller, *args):
        if controller.is_model():
            func(controller, *args)
        else:
            messagebox.showerror("Error", "No has carregat una imatge vàlida")

    return wrapper


class Controller:

    def __init__(self, view: gui.View):
        self.__view = view
        self.__model = None
        self.__depth = 0

        self.__position_first = None
        self.__view.set_functions(file_o=self.open_file, header_s=self.show_headers,
                                  depth=self.change_depth, zoom=self.change_zoom,
                                  movements=[self.initial_movement, self.movement],
                                  histogram=self.histogram_movement, adv_viewer=self.show_adv_image,
                                  histogram_release=self.realease_line,
                                  pixel_value=('<Motion>', self.position_value),
                                  distance=('<Button-3>', self.distance))

        self.__h_last_mouse_pos = None
        self.__selected_line = None

        self.__selected_point = None
        self.__distance_selected_point = None

    @exist_model
    def show_adv_image(self):
        plt.figure()
        plt.imshow(self.__model[self.__depth])
        plt.show()

    def is_model(self) -> bool:
        return self.__model is not None

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Dicom files", "*.dcm")]
        )
        if filepath:
            self.__model = DicomImage(filepath)
            self.__view.show_image(self.__model[0], histogram=self.__model.get_histogram(0))
            self.__view.set_n_images(len(self.__model))
        self.__view.title(f"DICOM Reader - {filepath}")

    @exist_model
    def show_headers(self):
        dades = []

        for h, v in self.__model.get_header():
            str_v = str(v)
            str_h = str(h)
            if hasattr(v, 'length'):
                if v.length > 200:
                    print(v.length)
                    str_v = str_v[:400]
            dades.append([str_h, str_v])
        tktable.make_table("Capceleres", dades)

    @exist_model
    def change_depth(self, value):
        depth = int(value) // 2
        self.__depth = depth

        self.__update_view_image(update_histogram=True)

    @exist_model
    def change_zoom(self, value):
        zoom = int(value)

        self.__model.resize_factor = zoom
        self.__update_view_image()

    @exist_model
    def initial_movement(self, event):
        self.__position_first = np.array([event.x, event.y])

    @exist_model
    def movement(self, event):
        assert self.__position_first is not None

        position = np.array([event.x, event.y])
        old_position = self.__position_first

        self.__position_first = None

        self.__model.move_image(old_position - position)
        self.__update_view_image()

    @exist_model
    def histogram_movement(self, event):
        new_pos = np.array([event.x, event.y - 1])
        last_pos = self.__h_last_mouse_pos

        idx_line = self.__selected_line
        if idx_line is None:
            idx_line, dist = self.__nearest_line(new_pos)
            if dist < 10:
                self.__selected_line = idx_line
            else:
                idx_line = None

        if last_pos is not None and idx_line is not None:
            diff = last_pos - new_pos
            direction = diff / np.abs(diff)
            self.__view.move_line(idx_line, front=(direction[0] > 0), velocity=np.abs(diff[0]))

        self.__h_last_mouse_pos = new_pos

    @exist_model
    def realease_line(self, event):
        self.__selected_line = None
        self.__h_last_mouse_pos = None

        histogram_bbox = self.__view.get_histogram_position()
        width = histogram_bbox[2] - histogram_bbox[0]

        horizontal_pos = [min((line[0] / width), 1) for line in self.__view.lines_position()]
        self.__model.contrast = horizontal_pos
        self.__update_view_image()

    def __nearest_line(self, position: np.ndarray):
        lines_pos = self.__view.lines_position()
        min_dist = None
        min_idx = None

        for idx, pos in enumerate(lines_pos):
            distance = math.sqrt(((pos[0] - position[0]) ** 2))

            if min_dist is None or distance < min_dist:
                min_dist = distance
                min_idx = idx

        return min_idx, min_dist

    def position_value(self, event):
        img_coordinates = self.__gui_coordinates_2_img_coordinates([event.x, event.y])
        if img_coordinates is not None:
            self.__view.set_pixel_text(
                str(self.__model.get_pixel(img_coordinates[0], img_coordinates[1], self.__depth)))

    @exist_model
    def distance(self, event):
        previous_point = self.__distance_selected_point
        actual_point = self.__gui_coordinates_2_img_coordinates([event.x, event.y])

        if previous_point is not None:
            self.__distance_selected_point = None

            actual_point = np.array(actual_point)
            previous_point = np.array(previous_point)

            distance = self.__model.get_distance(actual_point, previous_point)
        else:
            self.__distance_selected_point = actual_point
            distance = None

        print(distance)
        # return distance

    def __gui_coordinates_2_img_coordinates(self, gui_coordinates: List[int]):
        """
        Converts GUI coordinates to img coordinates.

        Args:
            gui_coordinates (List[int]):

        Returns:

        """
        img_coordinates = None
        if self.is_model():
            bbox = self.__view.get_image_position()

            if 0 < gui_coordinates[0] < (bbox[2] - bbox[0]) and 0 < gui_coordinates[1] < (
                    bbox[3] - bbox[1]):
                img_coordinates = [(gui_coordinates[0] - bbox[0]), (gui_coordinates[1] - bbox[1])]

        return img_coordinates

    def __update_view_image(self, update_histogram=False):
        depth = self.__depth

        histogram = self.__model.get_histogram(depth)

        if self.__model is not None and depth < len(self.__model):
            self.__view.show_image(self.__model[depth], histogram)

    def start(self):
        self.__view.draw()
