import os
import glob
import shelve

from backups.scanners.base_scanner import BaseScanner
from logs.models import BackupLogger
from becky.utils import remove_prefix, path_to_folders

"""
Scanner to scan files from the own local system.
Generates its own small shelve database where to host
its results.
"""

class LocalFilesScanner(BaseScanner):
    
        def __init__(self, parameters, state_database, backup_model):
            self.parameters = parameters
            self.logger = BackupLogger(backup_model)
            self.db = state_database
            self.backup_model = backup_model
            self.tag = 'LocalFilesScanner'

        def get_changed_files(self):
            """
            Retrieves all found files to be backed up from the database.
            """
            self.db.open_connection(self.tag)
            new_files = list(self.db.get('new_files'))
            self.db.close_connection()
            return new_files

        def mark_new_files(self):
            """
            Marks new files as backed up files.
            """
            self.db.open_connection(self.tag)
            backed_up_files = self.db.get('backed_up_files', [])
            new_files = self.db.get('new_files', [])
            backed_up_files = backed_up_files + new_files
            self.db.save('backed_up_files', backed_up_files)
            self.db.save('new_files', [])
            self._log('INFO', 'Marked {} files as backed up. Now {} files in total.'.format(len(new_files), len(backed_up_files)))
            self.db.close_connection()


        def scan_files(self, backup_files):
            """
            Starts the file scanning procedure.
            Looks at the path from the parameters to see where 
            it should start scanning for files to be backed up.
            """
            self._log('INFO', 'Started file scanning.')
            scanned_files = []
            for backup_file_i, backup_file in enumerate(backup_files):
                self.backup_model.set_status(status_message='Scanning for files from {} \t {} files found so far...'.format(backup_file.path, len(scanned_files)), percentage=int((backup_file_i / len(backup_files))*100), running=True)
                self._log('DEBUG', 'Scanning for files from selected path {}'.format(backup_file.path))
                scanned_files += self._scan_local_files(backup_file)
            self.backup_model.set_status(status_message='Files found in total {}...'.format(len(scanned_files)), percentage=100, running=True)
            scanned_files = list(set(scanned_files))
            scanned_files = self.backup_model.create_backup_file_instances(scanned_files)
            self._log('INFO', 'Finished file scanning.')
            self._log('INFO', 'Starting file comparisions.')
            self._compare_scanned_files(scanned_files)

        def _scan_local_files(self, backup_file):
            """
            Uses glob to recursively find all files from the starting_path.
            TODO: What if the the glob output becomes massive?
            """
            if os.path.isfile(backup_file.path): # Starting_path is not a folder, but a file
                implicit_folders = path_to_folders(backup_file.path)
                scanned_files = implicit_folders
                # scanned_files = self.backup_model.create_backup_file_instances(implicit_folders)
            else:
                scanned_files = glob.glob(backup_file.path + "/**/*", recursive=True)
                implicit_folders = path_to_folders(backup_file.path)
                scanned_files  = implicit_folders + scanned_files
                # scanned_files = self.backup_model.create_backup_file_instances(scanned_files)
            return scanned_files

        def _compare_scanned_files(self, scanned_files):
            """
            Compares the scanned files with the files from the database.
            For now, only checks whether there are any files that are NOT
            present in the database. Any changes to previously backed up files
            would therefore not be backed up, ever.
            """
            self.db.open_connection(self.tag)
            files = self.db.get('backed_up_files', [])
            backed_up_paths = set([f.path for f in files])
            new_files = []
            for new_file_i, new_file in enumerate(scanned_files):
                if new_file.path not in backed_up_paths:
                    new_files.append(new_file)
                if new_file_i % 100 == 0:
                    self.backup_model.set_status(status_message='Comparing found files with backed up files. \t {} new files have been found so far.'.format(len(new_files)), percentage=int((new_file_i / len(scanned_files))*100), running=True)
            self.db.save('new_files', new_files)
            self._log('INFO', 'Found {} new files.'.format(len(new_files)))
            self.db.close_connection()

        def _log(self, level, message):
            """
            Helper method to log events.
            Uses the logger provided on initialization to add logs.
            """
            self.logger.log(message=message, level=level, tag=self.tag)

