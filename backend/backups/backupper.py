"""

This is the main backupper class in charge of running a backup.
It handles the local database generation and scanning, but the actual
backupping is off-loaded to provider specific implementations.

"""

import backups.providers as providers
import backups.scanners as scanners
from logs.models import BackupLogger

class Backupper:

    def __init__(self, backup_model):
        self.backup_model = backup_model
        self.logger = self._get_logger()
        self.backup_provider = self._get_backup_provider()
        self.scanner = self._get_file_scanner()

    def backup(self):
        """
        Starts the backup process. If this is the first time running it,
        it first generates the database and then backups everything.
        On subsequent runs it just scans for new/changed files and scans those.
        """
        print("Starting file scanning...")
        self.scanner.scan_files()
        print("Starting file backing...")
        self.backup_provider.backup_files(self.scanner.get_changed_files())
        print("Starting file marking...")
        self.scanner.mark_new_files()
        return True

    def _get_backup_provider(self):
        """
        Checks the desired backup provider from the model and intializes a proper 
        backup provider model.
        """
        backup_provider = self.backup_model.get_backup_provider()
        parameters = self.backup_model.get_provider_parameters()
        if backup_provider == 'local':
            provider = providers.local_provider.LocalBackupProvider(parameters, self.logger)
        return provider

    def _get_file_scanner(self):
        """
        Returns a scanner object that will be used to scan new / changed files on the system.
        """
        parameters = self.backup_model.get_provider_parameters()
        scanner = scanners.local_scanner.LocalFilesScanner(parameters, self.logger)
        return scanner


    def _get_logger(self):
        """
        Returns a logger object that other objects can and will use to log their events.
        TODO: For now, just using the default logger. At someone allow using different loggers as well?
        """
        logger = BackupLogger(self.backup_model)
        return logger
