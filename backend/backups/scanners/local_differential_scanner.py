import os
import glob
import shelve
import pathlib
import datetime

from django.db import models, transaction
from django.utils.timezone import make_aware

from backups.scanners.base_scanner import BaseScanner
from backups.models import DifferentialInformation
from logs.models import BackupLogger
from becky.utils import remove_prefix, path_to_folders

"""
Scanner to scan files from the own local system.
Scans file differentially, so any file that 
has changed since previous scan will be flagged for
copying.
"""

class LocalDifferentialScanner(BaseScanner):
    
        def __init__(self, parameters, backup_model):
            self.parameters = parameters
            self.logger = BackupLogger(backup_model)
            self.backup_model = backup_model
            self.tag = 'LocalDifferentialScanner'

        def scan_files(self, backup_files, current_timestamp):
            """
            Starts the file scanning procedure.
            Looks at the path from the parameters to see where 
            it should start scanning for files to be backed up.
            Checks the previous modified date of a file to see if 
            it needs to be backed up again.
            """
            self._log('INFO', 'Started file scanning.')
            scanned_files = []
            for backup_file_i, backup_file in enumerate(backup_files):
                self.backup_model.set_status(status_message='Scanning for files from {} \t {} files found so far...'.format(backup_file.path, len(scanned_files)), percentage=int((backup_file_i / len(backup_files))*100), running=True)
                self._log('DEBUG', 'Scanning for files from selected path {}'.format(backup_file.path))
                scanned_files += self._scan_local_files(backup_file)
            scanned_files = list(set(scanned_files))
            diff_info = self._get_differential_information(scanned_files)
            self.backup_model.set_status(status_message='Files found in total {}...'.format(len(scanned_files)), percentage=100, running=True)
            scanned_files = self.backup_model.create_backup_file_instances(scanned_files, current_timestamp)
            current_files = self.backup_model.get_all_backup_items()
            self._log('INFO', 'Finished file scanning.')
            self._log('INFO', 'Starting file comparisions.')
            return self._compare_scanned_files(scanned_files, diff_info)


        def _get_differential_information(self, files):
            diffs = []
            with transaction.atomic():
                for f in files:
                    found_diff, created = DifferentialInformation.objects.get_or_create(backup=self.backup_model, path=f)
                    current_modified = int(os.path.getmtime(f))
                    current_modified = make_aware(datetime.datetime.fromtimestamp(current_modified))
                    found_diff.previous_modified = found_diff.current_modified
                    found_diff.current_modified = current_modified
                    found_diff.save()
                    diffs.append(found_diff)
            return diffs

        def _scan_local_files(self, backup_file):
            """
            Uses glob to recursively find all files from the starting_path.
            TODO: What if the the glob output becomes massive?
            """
            if not os.path.exists(backup_file.path):
                return []
            if os.path.isfile(backup_file.path): # Starting_path is not a folder, but a file
                scanned_files = path_to_folders(backup_file.path) + [backup_file.path]
            else:
                scanned_files = path_to_folders(backup_file.path) + self._walk_folders(backup_file.path)
                scanned_files = scanned_files
            return scanned_files

        def _compare_scanned_files(self, scanned_files, diff_info):
            """
            Compares the scanned files with the files from the database.
            Uses diff info to see if the scanned file has been modified since last scan
            and thus would require re-backing up.
            """
            new_files = []
            for i, diff in enumerate(diff_info):
                if diff.previous_modified == None: # First time seeing this file
                    new_files.append(scanned_files[i])
                else:
                    if diff.previous_modified != diff.current_modified:
                        new_files.append(scanned_files[i])
                if i % 100 == 0:
                    self.backup_model.set_status(status_message='Comparing found files with backed up files. \t {} new files have been found so far.'.format(len(new_files)), percentage=int((i / len(scanned_files))*100), running=True)
            self._log('INFO', 'Found {} new files.'.format(len(new_files)))
            return new_files

        def _log(self, level, message):
            """
            Helper method to log events.
            Uses the logger provided on initialization to add logs.
            """
            self.logger.log(message=message, level=level, tag=self.tag)


        def _walk_folders(self, path):
            """
            Uses os.walk to get all files in the given path.
            """
            files = set()
            for root, directories, dir_files in os.walk(path):
                files.add(root)
                for f in dir_files:
                    files.add(os.path.join(root, f))
                    self.backup_model.set_status(status_message='Scanning for files from {} \t {} files found so far...'.format(path, len(files)), percentage=None, running=True)
                    if len(files) % 100 == 0:
                        self._log('DEBUG', 'Found {} new files from {}.'.format(len(files), path))
            return list(files)
