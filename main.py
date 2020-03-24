from view import gui
from controller.controller import Controller


def main():
    vw = gui.View("DICOM Reader")
    contr = Controller(vw)
    contr.start()


main()
