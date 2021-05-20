import os
import glob
import shelve
import tempfile
import uuid
from shutil import copyfile
import backups.providers.exceptions as exceptions
from backups.providers.base_provider import BaseProvider
from logs.models import BackupLogger
from becky.utils import remove_prefix, join_file_path, path_to_folders

"""
A remote backup provider that can backup files from the local system
to a remote server in a differential fashion.
"""
class DifferentialRemoteProvider(BaseProvider):
    
    def __init__(self, parameters, backup_model):
        self.parameters = parameters
        self.backup_model = backup_model
        self.logger = BackupLogger(backup_model)
        self.tag = 'DifferentialRemoteBackupProvider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        """
        self._log('INFO', 'Started backing up files.')
        list_of_files.sort(key=lambda x: len(x.path)) # Sort, so folders will be created before any files are copied in.
        remote_addr = self._get_parameter('remote_addr')
        remote_copy_path = self._get_parameter('remote_path')
        ssh_identity_path = self._get_parameter('ssh_id_path')

        self._log('DEBUG', 'Saving files to {}/{}'.format(remote_addr, remote_copy_path))
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))
        self.backup_model.set_status('Starting to copy files. \t Files copied so far {}/{}'.format(0, len(list_of_files)), 0, True)

        saved_files = []
        files_to_copy = []
        for file_in_index, file_in in enumerate(list_of_files):
            files_to_copy.append(file_in)
            if file_in.file_type == 'directory': continue # We don't save directories
            file_out = self._generate_output_path(file_in, remote_copy_path)

        self._copy_files(files_to_copy, remote_addr, remote_copy_path, ssh_identity_path)
        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))
        return files_to_copy

    def restore_files(self, selections, restore_path, **kwargs):
        """
        Restores selected files from the backups to the restore folder.
        """
        self._log('INFO', 'Starting file restore process.') 
        remote_addr = self._get_parameter('remote_addr')
        remote_copy_path = self._get_parameter('remote_path')
        ssh_identity_path = self._get_parameter('ssh_id_path')

        files_to_restore = []
        for selection in selections:
            selection_files = path_to_folders(selection.path) + glob.glob(selection.path + "/**/*", recursive=True)
            files_to_restore += selection_files
        self._log('INFO', '{} files/folders to restore.'.format(len(files_to_restore)))
        files_to_restore = list(set(files_to_restore))
        files_to_restore.sort(key=len)
        files_to_copy = []
        for selection_file in files_to_restore:
            backup_file = self.backup_model.create_backup_file_instance(selection_file)
            files_to_copy.append(backup_file)
        self._copy_remote_files(files_to_copy, restore_path, remote_addr, remote_copy_path, ssh_identity_path)
        self._log('INFO', '{} files/folders restored.'.format(len(files_to_restore)))

    def verify_files(self):
        """
        Verifies that the the internal state of BackupItems matches the remote files.
        Returns true if eveything is ok, else returns False.
        """
        backup_items = self.backup_model.get_all_backup_items()
        remote_copy_path = self._get_parameter('remote_path')
        remote_paths = [join_file_path(remote_copy_path, backup_item.path) for backup_item in backup_items]
        remote_checksums = self._get_remote_checksums(remote_paths)
        mismatched_files = set()
        for backup_item_i, backup_item in enumerate(backup_items):
            if backup_item.checksum != remote_checksums.get(join_file_path(remote_copy_path, backup_item.path), '0'):
                mismatched_files.add(backup_item.path)
        if len(mismatched_files) > 0:
            raise exceptions.DataVerificationFailedException(fail_count=len(mismatched_files))

    def get_remote_files(self, path, **kwargs):
        """
        Returns all remote files at the given path. 
        """
        files = self.backup_model.backup_items.filter(directory=path)
        return files



    def _get_parameter(self, key):
        """
        Returns the parameter with the given key from the backup parameters.
        """
        return self.parameters['providerSettings'][key]

    def _get_remote_checksums(self, remote_paths):
        """
        Runs checksums on the remote server on the given paths.
        Process:
            1. Copies the list of files to run checksum to the server.
            2. Runs md5sum on each file on the remote server and save results to tmp.
            3. Copy back the results.
        TODO: Maybe use an actual SSH client to do this without any file saving.
        """
        remote_addr = self._get_parameter('remote_addr')
        remote_copy_path = self._get_parameter('remote_path')
        ssh_identity_path = self._get_parameter('ssh_id_path')

        remote_paths_file = '/tmp/{}'.format(str(uuid.uuid4()))
        remote_checksums_file = '/tmp/{}'.format(str(uuid.uuid4()))
        open(remote_paths_file, "w").write('\n'.join(remote_paths) + '\n')
        command = 'scp -i {} {} {}:{} > /dev/null'.format(ssh_identity_path, remote_paths_file, remote_addr, remote_paths_file)
        os.system(command)
        command = "ssh -i {} {} 'while read line; do md5sum $line; done < {} > {} 2>/dev/null' > /dev/null".format(ssh_identity_path, remote_addr, remote_paths_file, remote_checksums_file)
        os.system(command)
        command = 'scp -i {} {}:{} {} > /dev/null'.format(ssh_identity_path, remote_addr, remote_checksums_file, remote_checksums_file)
        os.system(command)
        checksum_lines = open(remote_checksums_file, "r").read().split('\n')
        checksums = {}
        checksum_lines = [l.strip() for l in checksum_lines if l.strip()]
        for checksum_i, checksum_line in enumerate(checksum_lines):
            checksum = checksum_line.split(" ")[0].strip()
            file_name = checksum_line.split(" ", 1)[1].strip()
            checksums[file_name] = checksum
        return checksums

    
    def _copy_files(self, files, remote_addr, remote_path, ssh_identity_path):
        """
        Copies a list of files from the current server to the remote server.
        Uses rsync to copy the files efficiently.
        """
        paths = [f.path for f in files]
        files_file = tempfile.NamedTemporaryFile(mode="w")
        files_file.write('\n'.join(paths))
        files_file.flush()
        command = 'rsync -e "ssh -i {}" --files-from {} / {}:{}'.format(ssh_identity_path, files_file.name, remote_addr, remote_path)
        os.system(command)
        files_file.close()

    def _copy_remote_files(self, files, restore_path, remote_addr, remote_path, ssh_identity_path):
        """
        Copies a list of files from the remote server to the current server in the specified restore folder.
        Uses rsync to copy the files efficiently.
        """
        paths = [f.path for f in files]
        files_file = tempfile.NamedTemporaryFile(mode="w")
        files_file.write('\n'.join(paths))
        files_file.flush()
        command = 'rsync -e "ssh -i {}" --files-from {} {}:{} {}'.format(ssh_identity_path, files_file.name, remote_addr, remote_path, restore_path)
        os.system(command)
        files_file.close()

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
