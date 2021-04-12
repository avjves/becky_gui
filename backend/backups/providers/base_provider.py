from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    def backup_files(self, list_of_files):
        """
        Receives a list of files that have to be backed up.
        """
        raise NotImplementedError
