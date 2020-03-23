from view import gui
from controller.controller import Controller


def main():
    vw = gui.View(None, "DICOM Reader")
    contr = Controller(vw)
    contr.start()


main()
