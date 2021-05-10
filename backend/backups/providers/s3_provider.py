import os
import glob
import shelve
import subprocess
from tempfile import TemporaryDirectory
from shutil import copyfile

import backups.providers.exceptions as exceptions
from backups.providers.base_provider import BaseProvider
from logs.models import BackupLogger
from becky.utils import remove_prefix, join_file_path, path_to_folders

"""
A provider that can backup to and from any S3 compatible object storage server.
"""
class S3Provider(BaseProvider):
    
    def __init__(self, parameters, backup_model):
        self.parameters = parameters
        self.backup_model = backup_model
        self.logger = BackupLogger(backup_model)
        self.tag = 'S3Provider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        TODO: Use rsync or something a bit more efficient than
        going through files one at a time.
        """
        list_of_files.sort(key=lambda x: len(x.path)) # Sort, so folders will be created before any files are copied in.
        self._log('INFO', 'Started backing up files.')

        bucket_name = self._get_parameter('bucket_name')
        self._log('DEBUG', 'Saving files to bucket {}'.format(bucket_name))
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))
        self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(0, len(list_of_files)), 0, True)
        saved_files = []
        for file_in_index, file_in in enumerate(list_of_files):
            file_out = self._generate_output_path(file_in, bucket_name)
            self._copy_file(file_in, file_out)
            saved_files.append(file_in)
            if file_in_index % 100 == 0:
                self._log('DEBUG', '{} new files backed up.'.format(file_in_index))
                self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(file_in_index, len(list_of_files)), int((file_in_index / len(list_of_files)) * 100), True)
        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))
        return saved_files

    def restore_files(self, selections, restore_path):
        """
        Restores selected files from the backups to the restore folder.
        """
        self._log('INFO', 'Starting file restore process.') 
        bucket_name = self._get_parameter('bucket_name')
        files_to_restore = []
        for selection in selections:
            selection_files = path_to_folders(selection.path) + glob.glob(selection.path + "/**/*", recursive=True)
            files_to_restore += selection_files
        self._log('INFO', '{} files/folders to restore.'.format(len(files_to_restore)))
        files_to_restore = list(set(files_to_restore))
        files_to_restore.sort(key=len)
        for selection_file in files_to_restore:
            backup_file = self.backup_model.get_backup_item(selection_file)
            restored_file = self.backup_model.create_backup_file_instance(join_file_path(restore_path, selection_file))
            self._restore_file(backup_file, restored_file, bucket_name)
        self._log('INFO', '{} files/folders restored.'.format(len(files_to_restore)))


    def verify_files(self):
        """
        Verifies that the the internal state of BackupItems matches the copied files on the s3 storage.
        """
        current_items = self.backup_model.get_all_backup_items()
        bucket_name = self._get_parameter('bucket_name')
        
        mismatched_files = set()
        for backup_item in current_items:
            if backup_item.file_type == 'directory': continue
            backup_path = self._generate_output_path(backup_item, bucket_name)
            result, err = self._run_command(['ls', '--list-md5', backup_path.path])
            matched = False
            if result.strip():
               splits = result.strip().split()
               if backup_item.checksum == splits[3]:
                   matched = True
            if not matched:
                mismatched_files.add(backup_item.path)
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
        Receives a single file that should be copied to the s3 object storage server.
        S3 doesn't have a concept of a directory, so we only have to copy the normal files themselves.
        """
        bucket_name = self._get_parameter('bucket_name')
        if os.path.exists(file_out.path):
            result, err = self._run_command(['ls', file_out.path])
            if result.strip(): # If we get any result from this LS command, said file already exists.
                return
        if os.path.isdir(file_in.path): # No need to copy files on s3 
            return
        result, err = self._run_command(['put', file_in.path, file_out.path])

    def _restore_file(self, backup_file, restored_file, bucket_name):
        """
        Restores a single file from the S3 storage to the given path.
        """
        backup_path = self._generate_output_path(backup_file, bucket_name)
        if backup_file.file_type == 'directory':
            os.makedirs(restored_file.path)
        else:
            result, err = self._run_command(['get', backup_path.path, restored_file.path])

    def _run_command(self, commands):
        """
        Given the command to run, runs it on the command line through s3cmd to the configured bucket.
        Returns whatever the command returns.
        """
        access_key = self._get_parameter('access_key')
        secret_key = self._get_parameter('secret_key')
        host = self._get_parameter('host')
        host_bucket = self._get_parameter('host_bucket')
        result = subprocess.run(['s3cmd'] + commands + ['--access_key', access_key, '--secret_key', secret_key, '--host', host, '--host-bucket', host_bucket], stdout=subprocess.PIPE)
        stdout = result.stdout.decode() if result.stdout else None
        stderr = result.stderr.decode() if result.stderr else None
        return stdout, stderr

    def _generate_output_path(self, file_in, bucket_name):
        """
        Generates an output path by concatenating copy_path and file_in.
        """
        file_out =  join_file_path('s3://', bucket_name, file_in.path)
        # self._log('DEBUG', 'Output path for {} is {}'.format(file_in.path, file_out))
        return self.backup_model.create_backup_file_instance(file_out)

    def _log(self, level, message):
        """
        Helper method to log events.
        Uses the logger provided on initialization to add logs.
        """
        self.logger.log(message=message, level=level, tag=self.tag)
