from pydicom.filereader import dcmread


class DicomImage:
    """
    Wrapper class for the pydicom library.

    The DicomImage is an iterable object though the different 3D channels

    """

    def __init__(self, path: str):
        self.__path = path
        self.__images = dcmread(path)

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        if self.__idx <= len(self):
            result = self.__images.pixel_array[:, :, self.__idx]
            self.__idx += 1
            return result
        else:
            raise StopIteration

    def __len__(self):
        return self.__images.pixel_array.shape[2]

    def __getitem__(self, item):
        return self.__images.pixel_array[:, :, item]

    def get_header(self):
        for k, v in self.__images.items():
            try:
                yield k, v
            except AttributeError:
                pass