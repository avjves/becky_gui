import os
import glob
import shelve
from shutil import copyfile
from django.db import models

import backups.providers.exceptions as exceptions
from backups.providers.base_provider import BaseProvider
from logs.models import BackupLogger
from becky.utils import remove_prefix, join_file_path, path_to_folders, calculate_checksum

"""
A local backup provider that can backup files differentially from one location
to another, within a local system.
On each subsequent update a changed file gets a new version saved.
"""

class DifferentialLocalProvider(BaseProvider):
    
    def __init__(self, parameters, backup_model):
        self.parameters = parameters
        self.backup_model = backup_model
        self.logger = BackupLogger(backup_model)
        self.tag = 'DifferentialBackupProvider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        """
        self._log('INFO', 'Started backing up files.')
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))

        copy_path = self._get_parameter('output_path')
        if not os.path.exists(copy_path):
            os.makedirs(copy_path)
        self._log('DEBUG', 'Saving files to {}'.format(copy_path))
        self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(0, len(list_of_files)), 0, True)
        saved_files = []
        for file_in_index, file_in in enumerate(list_of_files):
            if os.path.isdir(file_in.path): continue

            file_out = self._generate_output_path(file_in, copy_path)
            self._copy_file(file_in, file_out)
            saved_files.append(file_in)

            if file_in_index % 100 == 0:
                self._log('DEBUG', '{} new files backed up.'.format(file_in_index))
                self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(file_in_index, len(list_of_files)), int((file_in_index / len(list_of_files)) * 100), True)

        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))
        return saved_files

    def restore_files(self, files_to_restore, restore_path, **kwargs):
        """
        Restores selected files from the backups to the restore folder.
        """
        self._log('INFO', 'Starting file restore process.') 
        copy_path = self._get_parameter('output_path')
        self._log('INFO', '{} files/folders to restore.'.format(len(files_to_restore)))
        restored_files = []
        for selection_item in files_to_restore:
            selection_item_path = join_file_path(copy_path, selection_item.savename)
            restored_file_path = join_file_path(restore_path, selection_item.path)
            self._restore_file(selection_item_path, restored_file_path)
            restored_files.append(selection_item.path)
        return restored_files
        self._log('INFO', '{} files/folders restored.'.format(len(files_to_restore)))

    def _restore_file(self, selection_item_path, restore_file_path):
        """
        Restores the given file to the given path, creating any necessary directories on the way.
        """
        folder = restore_file_path.rsplit('/', 1)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self._log('DEBUG', 'Copying file {} to {}.'.format(selection_item_path, restore_file_path))
        copyfile(selection_item_path, restore_file_path)


    def verify_files(self):
        """
        Verifies that the the internal state of BackupItems matches the copied files on the local file system.
        Returns true if eveything is ok, else returns False.
        """
        current_items = self.backup_model.get_all_backup_items()
        copy_path = self._get_parameter('output_path')

        mismatched_files = set()
        matched_files = set()
        for backup_item in current_items:
            backup_file_path = join_file_path(copy_path, backup_item.savename)
            backup_file_checksum = calculate_checksum(backup_file_path)
            if backup_item.checksum != backup_file_checksum:
                mismatched_files.add(backup_item.path)
                self._log('DEBUG', 'File {} failed the verification process.'.format(backup_item.path))
            else:
                matched_files.add(backup_item.path)
        if len(mismatched_files) > 0:
            self._log('INFO', "Found {} files that didn't pass the verification process.".format(len(mismatched_files)))
            raise exceptions.DataVerificationFailedException(fail_count=len(mismatched_files))
        self._log('INFO', "Found {} files that passed verification process.".format(len(matched_files)))

    def _get_parameter(self, key):
        """
        Returns the parameter with the given key from the backup parameters.
        """
        return self.parameters['providerSettings'][key]
    

    def _copy_file(self, file_in, file_out):
        """
        Receives a single file that should be copied to the copy folder.
        """
        copyfile(file_in.path, file_out.path)

    def _generate_output_path(self, file_in, copy_path):
        """
        Generates an output path for the new file.
        Takes in account the creation time as well as the absolute path of the input file.
        """
        new_file_name = file_in.savename
        file_out =  join_file_path(copy_path, new_file_name)
        # self._log('DEBUG', 'Output path for {} is {}'.format(file_in.path, file_out))
        return self.backup_model.create_backup_file_instance(file_out)

    def _log(self, level, message):
        """
        Helper method to log events.
        Uses the logger provided on initialization to add logs.
        """
        self.logger.log(message=message, level=level, tag=self.tag)
