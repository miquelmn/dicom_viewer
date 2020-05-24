# -*- coding: utf-8 -*-
""" Controller of the MVC pattern.

This modules is the one that connects the model (model.DicomImage) with the View (view.GUI). Most of
the functions that contains this module are event handler detected on the GUI class.


"""
import math
from typing import List
import time
from tkinter import filedialog, messagebox
import os
import pkg_resources
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from viewer.view import tktable, gui
from viewer.model.dicom_files import DicomImage, Interpolation, Optimizer, Similarity


def exist_model(func):
    """ Decorator, check if the model is already loaded.

    Args:
        func:

    Returns:

    """

    def wrapper(controller, *args):
        if controller.check_model():
            func(controller, *args)
        else:
            messagebox.showerror("Error", "No has carregat una imatge vàlida")

    return wrapper


def long_process(func):
    """ Decorator. Shows a message after the function is finished.

    Args:
        func:

    Returns:

    """

    def wrapper(controller, *args):
        func(controller, *args)
        messagebox.showinfo('Info', "Procés acabat!")

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
        controller.update_status("Inici de la funció " + name)
        func(controller, *args)
        controller.update_status("Final de la funció " + name)

    return wrapper


LOOKUP = []


def load_lookup():
    """ Load into the global variable the lookup table for the header.

    Returns:

    """
    global LOOKUP

    if not LOOKUP:
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
                                  register=self.start_registration, alpha=self.start_fusion,
                                  Visualitzador_avançat=self.show_adv_image,
                                  Obrir_fitxer=lambda: self.__open_file(),
                                  Obrir_carpeta=lambda: self.__open_file(False),
                                  Rota_90=self.rotate, Swap_viewers=self.swap_viewers,
                                  Capceleres=self.show_headers, Historial=self.show_history,
                                  Watershed=self.watershed)

        self.__position_first = None

        self.__h_last_mouse_pos = None
        self.__selected_line = None

        self.__selected_point = None
        self.__distance_selected_point = None
        self.__history = []
        self.__flag_watershed = False
        self.__markers = []
        self.__mask = None

        self.__fusion = False

    @exist_model
    @save_actions
    def start_fusion(self):
        self.__fusion = True
        self.update_view_image()

    def update_iteration(self, method):
        self.__view.update_status_bar(
            "{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                             method.GetMetricValue(),
                                             method.GetOptimizerPosition()))
        self.__view.update()

    def __get_fusion(self, depth):
        alpha = self.__view.alpha

        cut_ref = self.__img_reference[depth]
        cut_inp = self.__img_input[depth]

        if cut_ref.shape[0] == cut_inp.shape[0] and cut_ref.shape[1] == cut_inp.shape[1]:
            cut_inp = cut_inp / cut_inp.max()
            cut_ref = cut_ref / cut_ref.max()

            res = [cut_ref * (1 - alpha), cut_inp * alpha, np.zeros_like(cut_ref)]

            res = np.dstack(res)

            res = res * 255
            res = res.astype(np.uint8)

            return res
        else:
            self.__fusion = False

            return None

    @exist_model
    @save_actions
    def rotate(self):
        """ Rotate the image 90 degrees.

        The whole 3D image is rotated 90 degrees from the center of the third dimension.

        Returns:

        """
        self.__img_reference.rotate()
        self.update_view_image()

    def update_status(self, status: str):
        """ Update status bar.

        Args:
            status:

        Returns:

        """
        self.__view.update_status_bar(status)
        self.__view.update()

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

    @exist_model
    @save_actions
    def start_registration(self):
        """ Start registration between model 1 and 2

        Returns:

        """

        if self.__img_input is None:
            raise Exception("Second image is not set")

        reg_fields = self.__view.registration_fields

        if len(reg_fields["Learning rate"]) > 0:
            lre = float(reg_fields["Learning rate"])
        else:
            lre = 0.0

        if len(reg_fields["Iterations"]) > 0:
            epochs = int(reg_fields["Iterations"])
        else:
            epochs = 1

        similarity = reg_fields["Similarity"]
        optimizer = reg_fields["Optimizer"]
        interpolation = reg_fields["Interpolation"]

        reg = self.__img_input.registration(self.__img_reference,
                                            optimizer=Optimizer.from_key(optimizer),
                                            similarity=Similarity.from_key(similarity),
                                            interpolation=Interpolation.from_key(interpolation),
                                            lre=lre, epochs=epochs,
                                            update_func=self.update_iteration)

        messagebox.showinfo("Mètrica",
                            "Corregistre finalitzat, mètrica " + reg_fields[
                                "Similarity"] + " = " + str(reg.GetMetricValue()))
        self.update_view_image()

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

    def check_model(self) -> bool:
        """ Check if the model is loaded

        Returns:

        """
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
            mask = self.__img_reference.apply_watershed(self.__markers)
            mask[mask == -1] = 0
            mask = mask.astype(float)
            mask = mask / mask.max()
            mask = mask * 255

            self.__mask = mask
            self.__view.set_text("Prova 1 \nProva 2")
            self.update_view_image()

        self.__markers = []
        self.__flag_watershed = not self.__flag_watershed

    @save_actions
    def __open_file(self, file: bool = True):
        """ Load and show Dicom image into the gui

        Args:
            file (bool):

        Returns:

        """
        self.__mask = None
        if file:
            filepath = filedialog.askopenfilename(initialdir="~",
                                                  filetypes=[("Dicom files", "*.dcm")])
        else:
            filepath = filedialog.askdirectory(initialdir="~")

        if filepath:
            image = DicomImage(filepath, self.__view.img_space)
            if self.__img_reference is not None and self.__img_input is None:
                histogram = None
                img_container = gui.ImageContID.secondary
                self.__img_input = image
            else:
                histogram = image.get_histogram(0)
                img_container = gui.ImageContID.principal
                self.__img_reference = image

            self.__view.show_image(image[0], img_container=img_container, histogram=histogram)
            self.__view.set_max_depth(len(image) - 1)
            self.__view.title(f"DICOM Reader - {filepath}")

    def swap_viewers(self):
        """ Swap the viewers

        Returns:

        """
        if self.__mask is not None:
            res = messagebox.askokcancel("Alerta",
                                         "Aquesta acció eliminarà la segementació existent")
            if not res:
                return
            self.__mask = None

        self.__img_input, self.__img_reference = self.__img_reference, self.__img_input
        self.update_view_image()

    @exist_model
    @save_actions
    def show_headers(self):
        """ Handler to show the headers of the Dicom-File

        Returns:

        """
        dades = []

        for header, value in self.__img_reference.get_header():
            str_v = str(value)
            str_h = str(header).replace(" ", "")
            if hasattr(value, 'length'):
                if value.length > 200:
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
    def change_zoom(self, value):
        """ Handler. Change the zoom of the image.

        Args:
            value:

        Returns:

        """
        zoom = int(value)

        if self.__img_reference is not None:
            self.__img_reference.resize_factor = zoom

        if self.__img_input is not None:
            self.__img_input.resize_factor = zoom

        self.update_view_image()

    @exist_model
    @save_actions
    def change_dim(self, value):
        """ Change the 3D point of view of the visualization.

        Args:
            value:

        Returns:

        """
        dim = 0
        if value == "First":
            dim = 0
        elif value == "Second":
            dim = 1
        elif value == "Third":
            dim = 2

        depth_1 = depth_2 = 1
        if self.__img_reference is not None and dim < len(self.__img_reference.shape):
            self.__img_reference.dim = dim
            depth_1 = len(self.__img_reference) - 1
        if self.__img_input is not None and dim < len(self.__img_input.shape):
            self.__img_input.dim = dim
            depth_2 = len(self.__img_input) - 1

        self.__view.set_max_depth(max(depth_1, depth_2), gui.ImageContID.principal)
        self.update_view_image()

    @exist_model
    def left_click(self, event):
        """ Handler. Handles the click of the principal mouse button.

        Args:
            event:

        Returns:

        """
        if self.__flag_watershed:
            coordinates = [0, 0, 0]
            not_used = [0, 1, 2]
            dim = self.__img_reference.dim

            coordinates[dim] = self.depth
            del not_used[dim]

            coordinates[min(not_used)] = event.y
            coordinates[max(not_used)] = event.x

            self.__markers.append(tuple(coordinates))
        else:
            self.__position_first = np.array([event.x, event.y])

    @exist_model
    @save_actions
    def movement(self, event):
        """ Handler. When is zoomed the images is moved.

        Args:
            event:

        Returns:

        """
        if not self.__flag_watershed:
            assert self.__position_first is not None

            position = np.array([event.x, event.y])
            old_position = self.__position_first

            self.__position_first = None

            self.__img_reference.move_image(old_position - position)

            if self.__img_input is not None:
                self.__img_input.move_image(old_position - position)

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
        if self.check_model():
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

        if self.__img_reference is not None and depth < len(self.__img_reference):
            histogram = self.__img_reference.get_histogram(depth)
            self.__view.show_image(self.__img_reference[depth], histogram)

        if self.__mask is not None and depth < len(self.__img_reference):
            self.__view.show_image(self.__get_mask(depth), img_container=gui.ImageContID.secondary)
        elif self.__mask is None and self.__img_input is not None and depth < len(self.__img_input):
            self.__view.show_image(self.__img_input[depth], img_container=gui.ImageContID.secondary)

        if self.__fusion:
            fusion = self.__get_fusion(depth)

            if fusion is not None:
                self.__view.show_image(fusion, img_container=gui.ImageContID.third)

    def __get_mask(self, item: int):
        """ Returns a cut of the mask

        Args:
            item:

        Returns:

        """
        if self.__mask is None:
            raise IndexError("Mask does not exist")

        dim = self.__img_reference.dim

        return self.__mask.take(indices=item, axis=dim)

    def start(self):
        """ Starts the app

        Returns:

        """
        load_lookup()
        self.__view.draw()
