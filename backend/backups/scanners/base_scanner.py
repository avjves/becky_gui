from abc import ABC, abstractmethod

class BaseScanner(ABC):

    @abstractmethod
    def scan_files(self):
        """
        Scans for files, save results to DB for later.
        """
        raise NotImplementedError

