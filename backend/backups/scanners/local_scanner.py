import os
import glob
import shelve

from backups.scanners.base_scanner import BaseScanner

"""
Scanner to scan files from the own local system.
Generates its own small shelve database where to host
its results.
"""

class LocalFilesScanner(BaseScanner):
    
        def __init__(self, parameters, logger):
            self.parameters = parameters
            self.logger = logger
            self.tag = 'LocalFilesScanner'

        def get_changed_files(self):
            """
            Retrieves all found files to be backed up from the database.
            """
            db = self._open_db_connection()
            new_files = list(db['new_files'])
            db.close()
            return new_files

        def mark_new_files(self):
            """
            Marks new files as backed up files.
            """
            db = self._open_db_connection()
            backed_up_files = db.get('backed_up_files', [])
            new_files = db.get('new_files', [])
            backed_up_files = backed_up_files + new_files
            db['backed_up_files'] = backed_up_files
            db['new_files'] = []
            self._log('INFO', 'Marked {} files as backed up. Now {} files in total.'.format(len(new_files), len(backed_up_files)))
            db.close()


        def scan_files(self):
            """
            Starts the file scanning procedure.
            Looks at the path from the parameters to see where 
            it should start scanning for files to be backed up.
            """
            self._log('INFO', 'Started file scanning.')
            # starting_path = self.parameters['path']
            starting_path = '/home/avjves/projects'
            scanned_files = self._scan_local_files(starting_path)
            self._log('INFO', 'Finished file scanning.')
            db = self._open_db_connection()
            self._log('INFO', 'Starting file comparisions.')
            self._compare_scanned_files(scanned_files, db)
            db.close()


        def _open_db_connection(self):
            """
            Checks whether its own database already exists or not
            and if it doesn't, it creates a new one.
            Returns a opened connection to said database.
            """
            # if not os.path.exists(self.parameters['database_location']):
            database_location = '/home/avjves/fs.sqlite3'
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

        def _compare_scanned_files(self, scanned_files, db):
            """
            Compares the scanned files with the files from the database.
            For now, only checks whether there are any files that are NOT
            present in the database. Any changes to previously backed up files
            would therefore not be backed up, ever.
            """
            files = db.get('backed_up_files', [])
            new_files = list(set(scanned_files).difference(set(files)))
            db['new_files'] = new_files
            self._log('INFO', 'Found {} new files.'.format(len(new_files)))

        def _log(self, level, message):
            """
            Helper method to log events.
            Uses the logger provided on initialization to add logs.
            """
            self.logger.log(message=message, level=level, tag=self.tag)

