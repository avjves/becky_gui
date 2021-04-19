import os
import glob
import shelve

from backups.scanners.base_scanner import BaseScanner
from logs.models import BackupLogger

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
            for file_path in backup_files:
                self._log('DEBUG', 'Scanning for files from selected path {}'.format(file_path))
            scanned_files += self._scan_local_files(file_path)
            self._log('INFO', 'Finished file scanning.')
            self._log('INFO', 'Starting file comparisions.')
            self._compare_scanned_files(scanned_files)


        def _open_db_connection(self):
            """
            Checks whether its own database already exists or not
            and if it doesn't, it creates a new one.
            Returns a opened connection to said database.
            """
            # if not os.path.exists(self.parameters['database_location']):
            # database_location = '/home/avjves/fs.sqlite3'
            database_location = '/home/avjves/dbs/{}.sqlite3'.format(self.backup_model.name)
            # if not os.path.exists(database_location):
            db = shelve.open(database_location)
            return db


        def _scan_local_files(self, starting_path):
            """
            Uses glob to recursively find all files from the starting_path.
            TODO: What if the the glob output becomes massive?
            """
            if os.path.isfile(starting_path): # Starting_path is not a folder, but a file
                scanned_files = [starting_path]
            else:
                scanned_files = glob.glob(starting_path + "/**/*", recursive=True)
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
            new_files = list(set(scanned_files).difference(set(files)))
            self.db.save('new_files', new_files)
            self._log('INFO', 'Found {} new files.'.format(len(new_files)))
            self.db.close_connection()

        def _log(self, level, message):
            """
            Helper method to log events.
            Uses the logger provided on initialization to add logs.
            """
            self.logger.log(message=message, level=level, tag=self.tag)

