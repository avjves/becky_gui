from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    def backup_files(self, list_of_files):
        """
        Receives a list of files that have to be backed up.
        """
        pass

    @abstractmethod
    def get_remote_files(self, path):
        """
        Returns the the names of backed up files at the given path.
        """
        pass

    @abstractmethod
    def restore_files(self, selections, restore_path):
        """
        Restores selected files from the backups to the restore folder.
        """
        pass
