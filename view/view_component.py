import abc


class VComponent(abc.ABC):

    def __init__(self):
        self.functions = None

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def set_function(self, **kwargs):
        pass
