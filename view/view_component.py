import abc


class VComponent(abc.ABC):

    def __init__(self):
        self.functions = None

    @abc.abstractmethod
    def draw(self):
        pass

    def set_function(self, functions):
        self.functions = functions
