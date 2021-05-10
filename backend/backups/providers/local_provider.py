import os
import glob
import shelve
from shutil import copyfile

import backups.providers.exceptions as exceptions
from backups.providers.base_provider import BaseProvider
from logs.models import BackupLogger
from becky.utils import remove_prefix, join_file_path, path_to_folders

"""
A local backup provider that can backup files from one location
to another, within a local system.
"""
class LocalProvider(BaseProvider):
    
    def __init__(self, parameters, backup_model):
        self.parameters = parameters
        self.backup_model = backup_model
        self.logger = BackupLogger(backup_model)
        self.tag = 'LocalBackupProvider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        TODO: Use rsync or something a bit more efficient than
        going through files one at a time.
        """
        self._log('INFO', 'Started backing up files.')
        list_of_files.sort(key=lambda x: len(x.path)) # Sort, so folders will be created before any files are copied in.

        copy_path = self._get_parameter('output_path')
        self._log('DEBUG', 'Saving files to {}'.format(copy_path))
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))
        self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(0, len(list_of_files)), 0, True)
        # remote_files = self.db.get(self.tag, 'remote_files', [])
        saved_files = []
        for file_in_index, file_in in enumerate(list_of_files):
            file_out = self._generate_output_path(file_in, copy_path)
            self._copy_file(file_in, file_out)
            # remote_files.append(file_in)
            saved_files.append(file_in)
            if file_in_index % 100 == 0:
                self._log('DEBUG', '{} new files backed up.'.format(file_in_index))
                self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(file_in_index, len(list_of_files)), int((file_in_index / len(list_of_files)) * 100), True)
        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))
        return saved_files
        # self.db.save(self.tag, 'remote_files', remote_files)

    def restore_files(self, selections, restore_path):
        """
        Restores selected files from the backups to the restore folder.
        """
        self._log('INFO', 'Starting file restore process.') 
        copy_path = self._get_parameter('output_path')
        files_to_restore = []
        for selection in selections:
            selection_files = path_to_folders(selection.path) + glob.glob(selection.path + "/**/*", recursive=True)
            files_to_restore += selection_files
        self._log('INFO', '{} files/folders to restore.'.format(len(files_to_restore)))
        files_to_restore = list(set(files_to_restore))
        files_to_restore.sort(key=len)
        for selection_file in files_to_restore:
            selection_file = self.backup_model.create_backup_file_instance(selection_file)
            restored_file = self._generate_output_path(selection_file, restore_path)
            backup_file = self.backup_model.create_backup_file_instance(selection_file.path)
            backup_file.path = join_file_path(copy_path, backup_file.path)
            # print("selection", selection_file.path, "backup_file", backup_file.path, "restored file", restored_file.path)
            # import pdb;pdb.set_trace()
            self._copy_file(backup_file, restored_file, create_folders=False)
        self._log('INFO', '{} files/folders restored.'.format(len(files_to_restore)))


    def verify_files(self):
        """
        Verifies that the the internal state of BackupItems matches the copied files on the local file system.
        Returns true if eveything is ok, else returns False.
        """
        current_items = self.backup_model.get_all_backup_items()
        copy_path = self._get_parameter('output_path')

        mismatched_files = set()
        for backup_item in current_items:
            backup_file_path = join_file_path(copy_path, backup_item.path)
            backup_file = self.backup_model.create_backup_file_instance(backup_file_path)
            backup_file.calculate_checksum()
            if backup_item.checksum != backup_file.checksum:
                mismatched_files.add(backup_item.path)
                # self._log('DEBUG', 'File {} failed the verification process.'.format(backup_item.path))
        if len(mismatched_files) > 0:
            self._log('INFO', "Found {} files that didn't pass the verification process.".format(len(mismatched_files)))
            raise exceptions.DataVerificationFailedException(fail_count=len(mismatched_files))
        self._log('INFO', "Verified {} files.".format(len(current_items) - len(mismatched_files)))    

    def _get_parameter(self, key):
        """
        Returns the parameter with the given key from the backup parameters.
        """
        return self.parameters['providerSettings'][key]
    

    def _copy_file(self, file_in, file_out, create_folders=False):
        """
        Receives a single file that should be copied to the copy folder.
        First checks that a proper folder exists before attempting a copy.
        If create_folders is true, creates all folders in the path.
        """
        if os.path.exists(file_out.path):
            return
        if os.path.isdir(file_in.path):
            os.makedirs(file_out.path)
            return
        if create_folders:
            folder = file_out.path.rsplit("/", 1)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
        copyfile(file_in.path, file_out.path)

    def _generate_output_path(self, file_in, copy_path):
        """
        Generates an output path by concatenating copy_path and file_in.
        """
        file_out =  join_file_path(copy_path, file_in.path)
        # self._log('DEBUG', 'Output path for {} is {}'.format(file_in.path, file_out))
        return self.backup_model.create_backup_file_instance(file_out)

    def _log(self, level, message):
        """
        Helper method to log events.
        Uses the logger provided on initialization to add logs.
        """
        self.logger.log(message=message, level=level, tag=self.tag)
