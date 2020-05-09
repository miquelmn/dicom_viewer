from viewer.model import dicom_files
from matplotlib import pyplot as plt


def main():
    menu = "*" * 50
    menu += "\n Dicom Viewer \n \t Miquel Miró Nicolau \n"
    menu += "*" * 50

    print(menu)
    while True:
        path = input("Path a la imatge (si vols sortir pitja s): \n")

        if path.lower() == "s":
            break

        dcm = dicom_files.DicomImage(path)

        print("*" * 50)
        tall = input("Quin tall vols veure ( 0 - " + str(len(dcm) - 1) + " ) ?")

        while tall.isdigit():
            tall = int(tall)
            plt.imshow(dcm[tall])
            plt.show()

            tall = input(
                "Si vols veure un altre tall indica el número sinó pitja una altre tecla per "
                "seleccionar una nova imatge ( 0 - " + str(len(dcm) - 1) + " ): \n")


main()
