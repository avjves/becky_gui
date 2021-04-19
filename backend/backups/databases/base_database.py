from abc import ABC, abstractmethod

class BaseDatabase(ABC):


    @abstractmethod
    def open_connection(self):
        pass


    @abstractmethod
    def close_connection(self):
        pass


    @abstractmethod
    def get(self, key):
        pass


    @abstractmethod
    def save(self, key, value):
        pass
