# -*- coding: utf-8 -*-
""" Controller of the MVC pattern.

This modules is the one that connects the model (model.DicomImage) with the View (view.GUI). Most of
the functions that contains this module are event handler detected on the GUI class.


"""
import math
from typing import List
import time
from tkinter import filedialog
import os
from tkinter import messagebox
import pkg_resources
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from viewer.view import tktable, gui
from viewer.model.dicom_files import DicomImage


def exist_model(func):
    """ Decorator, check if the model is already loaded.

    Args:
        func:

    Returns:

    """

    def wrapper(controller, *args):
        if controller.is_model():
            func(controller, *args)
        else:
            messagebox.showerror("Error", "No has carregat una imatge vàlida")

    return wrapper


def save_actions(func):
    """ Decorator, saves the actions made to a history

    Args:
        func:

    Returns:

    """
    name = func.__name__

    def wrapper(controller, *args):
        date = time.strftime("%H:%M:%S")
        str_args = ""
        for arg in args:
            str_args += str(arg)
        row = [date, name, str_args]
        controller.add_2_history(row)
        func(controller, *args)

    return wrapper


LOOKUP = []


def load_lookup():
    """ Load into the global variable the lookup table for the header.

    Returns:

    """
    global LOOKUP

    if LOOKUP is None:
        path = pkg_resources.resource_filename(
            __name__,
            os.path.join(os.pardir, 'resources', 'lookup.ods')
        )

        data_frame = pd.read_excel(path, engine="odf")
        data_frame = data_frame[["Tag", "Name"]]
        LOOKUP = data_frame.set_index('Tag').T.to_dict('list')


class Controller:
    """ Controller of the MVC design pattern

    """

    def __init__(self, view: gui.View):
        self.__view = view
        self.__img_reference = None
        self.__img_input = None

        self.__view.set_functions(movements=[self.left_click, self.movement],
                                  depth=self.update_view_image, zoom=self.change_zoom,
                                  histogram=self.histogram_movement,
                                  histogram_release=self.move_histogram,
                                  pixel_value=('<Motion>', self.position_value),
                                  distance=('<Button-3>', self.calc_distance),
                                  sel_dim=(["First", "Second", "Third"], self.change_dim),
                                  Visualitzador_avançat=self.show_adv_image,
                                  Obrir_fitxer=lambda: self.__open_file(gui.ImageContID.principal),
                                  Obrir_carpeta=lambda: self.__open_file(gui.ImageContID.principal,
                                                                         False),
                                  Capceleres=self.show_headers,
                                  Historial=self.show_history, Watershed=self.watershed,
                                  Second_image=lambda: self.__open_file(gui.ImageContID.secondary),
                                  Corregister=self.start_corregistration)

        self.__position_first = None

        self.__h_last_mouse_pos = None
        self.__selected_line = None

        self.__selected_point = None
        self.__distance_selected_point = None
        self.__history = []
        self.__flag_watershed = False
        self.__markers = []

    def add_2_history(self, row):
        """ Add new element to history.

        A history of actions is a set of ordered actions done by the user. This function adds a new
        action to this history.

        Args:
            row:

        Returns:

        """
        self.__history.append(row)

    @property
    def depth(self):
        """ Returns the actual depth selected

        Returns:

        """
        depth = self.__view.depth

        if isinstance(depth, tuple):
            depth = depth[0]

        return depth

    @property
    def reference_depth(self):
        """ Depth of the reference image.

        Returns:

        """
        depth = self.__view.depth

        if not isinstance(depth, list):
            return -1

        return depth[1]

    @exist_model
    def start_corregistration(self):
        """ Start corregistration between model 1 and 2

        Returns:

        """

        pass

    @exist_model
    @save_actions
    def show_adv_image(self):
        """ Show the actual image with Matplotlib.

        Returns:
            None
        """
        plt.figure()
        plt.imshow(self.__img_reference[self.depth])
        plt.show()

    def is_model(self) -> bool:
        return self.__img_reference is not None

    @exist_model
    @save_actions
    def watershed(self):
        """ Applies the watershed algorithm to the model image.

        This function uses the watershed algorithm with initial markers. The markers should already
        be set when this function is called. If the markers are not set a message box is shown to
        the user.

        Once the watershed is applied from each region a set of texture features is extracted.

        Returns:

        """

        if self.__flag_watershed and not self.__markers:
            messagebox.showerror("Error", "No has seleccionat marcadors inicials")
        elif self.__flag_watershed:
            mask = self.__img_reference.apply_watershed(self.depth, self.__markers)
            mask[mask == -1] = 0
            mask = mask.astype(float)
            mask = mask / mask.max()
            mask = mask * 255

            self.__view.show_image(mask, img_container=gui.ImageContID.secondary)
            self.__view.set_text("Prova 1 \nProva 2")

        self.__markers = []
        self.__flag_watershed = not self.__flag_watershed

    @save_actions
    def __open_file(self, img_container: gui.ImageContID, file: bool = True):
        """ Load and show Dicom image into the gui

        Args:
            img_container (gui.ImageContID) : Identifier to the container to thread.

        Returns:

        """
        if file:
            filepath = filedialog.askopenfilename(initialdir="~",
                                                  filetypes=[("Dicom files", "*.dcm")])
        else:
            filepath = filedialog.askdirectory(initialdir="~")

        if filepath:
            image = DicomImage(filepath, self.__view.img_space)
            if img_container is gui.ImageContID.principal:
                histogram = image.get_histogram(0)
                self.__img_reference = image
            else:
                histogram = None
                self.__img_input = image

            self.__view.show_image(image[0], img_container=img_container, histogram=histogram)
            self.__view.set_max_depth(len(image) - 1)
            self.__view.title(f"DICOM Reader - {filepath}")

    @exist_model
    @save_actions
    def show_headers(self):
        """ Handler to show the headers of the Dicom-File

        Returns:

        """
        global LOOKUP
        dades = []

        for h, v in self.__img_reference.get_header():
            str_v = str(v)
            str_h = str(h).replace(" ", "")
            if hasattr(v, 'length'):
                if v.length > 200:
                    str_v = str_v[:400]
            if str_h in LOOKUP:
                str_h = LOOKUP[str_h][0]
            dades.append([str_h, str_v])
        tktable.make_table("Capceleres", dades, ["Clau", "Valor"])

    def show_history(self):
        """ Handler. Shows the history of action to the user.

        Returns:

        """
        tktable.make_table("History", self.__history, ["Temps", "Funció", 'Parametres'])

    @exist_model
    @save_actions
    def change_zoom(self, value):
        """ Handler. Change the zoom of the image.

        Args:
            value:

        Returns:

        """
        zoom = int(value)

        self.__img_reference.resize_factor = zoom
        self.update_view_image()

    @exist_model
    @save_actions
    def change_dim(self, value, img_container: gui.ImageContID = gui.ImageContID.principal):
        """ Change the 3D point of view of the visualization.

        Args:
            value:
            img_container:

        Returns:

        """
        dim = 0
        if value == "First":
            dim = 0
        elif value == "Second":
            dim = 1
        elif value == "Third":
            dim = 2

        if img_container is gui.ImageContID.secondary:
            image = self.__img_input
        else:
            image = self.__img_reference

        image.dim = dim
        self.__view.set_max_depth(len(self.__img_reference) - 1, img_container)
        self.update_view_image()

    @exist_model
    def left_click(self, event):
        """ Handler. Handles the click of the principal mouse button.

        Args:
            event:

        Returns:

        """
        if self.__flag_watershed:
            self.__markers.append((event.y, event.x))
        else:
            self.__position_first = np.array([event.x, event.y])

    @exist_model
    @save_actions
    def movement(self, event):
        if not self.__flag_watershed:
            assert self.__position_first is not None

            position = np.array([event.x, event.y])
            old_position = self.__position_first

            self.__position_first = None

            self.__img_reference.move_image(old_position - position)
            self.update_view_image()

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
    @save_actions
    def move_histogram(self, event):
        """ Handler of the movement of the line on the histogram.

        Args:
            event:

        Returns:

        """
        self.__selected_line = None
        self.__h_last_mouse_pos = None

        histogram_bbox = self.__view.get_histogram_position()
        width = histogram_bbox[2] - histogram_bbox[0]

        horizontal_pos = [min((line[0] / width), 1) for line in self.__view.lines_position()]
        self.__img_reference.contrast = horizontal_pos
        self.update_view_image()

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
        """ Get the value of the pixel located under the mouse

        Args:
            event:

        Returns:

        """
        img_coordinates = self.__gui_coordinates_2_img_coordinates([event.x, event.y])
        if img_coordinates is not None:
            self.__view.set_pixel_text(
                str(self.__img_reference.get_voxel(img_coordinates[0], img_coordinates[1],
                                                   self.depth)))

    @exist_model
    @save_actions
    def calc_distance(self, event):
        """ Calculate distance between two points.

        Args:
            event:

        Returns:

        """
        previous_point = self.__distance_selected_point
        actual_point = self.__gui_coordinates_2_img_coordinates([event.x, event.y])
        distance = None

        if previous_point is not None and actual_point is not None:
            self.__distance_selected_point = None

            actual_point = np.array(actual_point)
            previous_point = np.array(previous_point)

            distance = self.__img_reference.get_distance(actual_point, previous_point)
        elif actual_point is not None:
            self.__distance_selected_point = actual_point

        if distance is not None:
            self.__view.set_distance_text(str(distance))

    def __gui_coordinates_2_img_coordinates(self, gui_coordinates: List[int]):
        """ Converts GUI coordinates to img coordinates.

        The GUI coordinates has its reference point from the origin (top, left) of the window. To
        get the correspondence between that coordinates and the image ones we should substract the
        position of the image.

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

    def update_view_image(self, value=None):
        """ Update the image from the view.

        Returns:

        """
        depth = self.depth

        histogram = self.__img_reference.get_histogram(depth)

        if self.__img_reference is not None and depth < len(self.__img_reference):
            self.__view.show_image(self.__img_reference[depth], histogram)

    def start(self):
        load_lookup()
        self.__view.draw()
