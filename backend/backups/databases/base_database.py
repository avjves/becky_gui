from abc import ABC, abstractmethod

class BaseDatabase(ABC):


    @abstractmethod
    def open_connection(self):
        pass


    @abstractmethod
    def close_connection(self):
        pass


    @abstractmethod
    def get(self, state_name, key):
        pass


    @abstractmethod
    def save(self, state_name, key, value):
        pass

    @abstractmethod
    def clear(self, state_name):
        pass
