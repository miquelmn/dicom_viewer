from viewer.view import gui
from viewer.controller.controller import Controller


def run():
    vw = gui.View("DICOM Reader")
    contr = Controller(vw)
    contr.start()