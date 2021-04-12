from abc import ABC, abstractmethod

class BaseScanner(ABC):

    @abstractmethod
    def scan_files(self):
        """
        Scans for files, save results to DB for later.
        """
        raise NotImplementedError

    @abstractmethod
    def get_changed_files(self):
        """
        Provides all files that require backing up since the last
        backup/scan.
        """
        raise NotImplementedError
