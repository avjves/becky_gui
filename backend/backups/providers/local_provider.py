import os
import shelve
from shutil import copyfile
from backups.providers.base_provider import BaseProvider
from logs.models import BackupLogger

"""
A local backup provider that can backup files from one location
to another, within a local system.
"""
class LocalProvider(BaseProvider):
    
    def __init__(self, parameters, state_database, backup_model):
        self.parameters = parameters
        self.backup_model = backup_model
        self.db = state_database
        self.logger = BackupLogger(backup_model)
        self.tag = 'LocalBackupProvider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        TODO: Use rsync or something a bit more efficient than
        going through files one at a time.
        """
        self._log('INFO', 'Started backing up files.')
        list_of_files.sort() # Sort, so folders will be created before any files are copied in.

        copy_path = self._get_parameter('output_path')
        self._log('DEBUG', 'Saving files to {}'.format(copy_path))
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))
        self.db.open_connection(self.tag)
        remote_filenames = self.db.get('remote_filenames', [])
        for file_in_index, file_in in enumerate(list_of_files):
            file_out = self._generate_output_path(file_in, copy_path)
            self._copy_file(file_in, file_out)
            remote_filenames.append(file_in)
            if file_in_index % 1000 == 0:
                self._log('DEBUG', '{} new files backed up.'.format(file_in_index))
        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))
        self.db.save('remote_filenames', remote_filenames)
        self.db.close_connection()

    def get_remote_files(self, path):
        """
        Returns the the names of backed up files at the given path.
        """
        print(path)
        self.db.open_connection(self.tag)
        remote_filenames = self.db.get('remote_filenames', [])
        ##TODO MAKE THIS BETTER
        remote_files_to_return = []
        for remote_filename in remote_filenames:
            remote_filename = remote_filename.replace(path, '/')
            folder, filename = remote_filename.rsplit('/', 1)
            folder
            if folder:
                remote_files_to_return.append(filename)
        self.db.close_connection()
        return remote_files_to_return

    def restore_files(self, selections, restore_path):
        """
        Restores selected files from the backups to the restore folder.
        """
        self._log('INFO', 'Starting file restore process.') 
        copy_path = self._get_parameter('output_path')
        self._log('INFO', '{} files/folders to restore.'.format(len(selections)))
        for selection in selections.keys():
            backup_file_path = self._generate_output_path(selection, copy_path)
            restore_file_path = os.path.join(restore_path, selection.strip('/'))
            self._copy_file(backup_file_path, restore_file_path)
        self._log('INFO', '{} files/folders restored.'.format(len(selections)))

    def _get_parameter(self, key):
        """
        Returns the parameter with the given key from the backup parameters.
        """
        return self.parameters['providerSettings'][key]
    

    def _copy_file(self, file_in, file_out):
        """
        Receives a single file that should be copied to the copy folder.
        First checks that a proper folder exists before attempting a copy.
        """
        if os.path.exists(file_out):
            return
        if os.path.isdir(file_in):
            os.makedirs(file_out)
            return
        folder = file_out.rsplit("/", 1)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        copyfile(file_in, file_out)

    def _generate_output_path(self, file_in, copy_path):
        """
        Strips unnecessary suffix from the file_in parameter using the starting path and 
        generates an output path for the file.
        """
        file_out =  os.path.join(copy_path, file_in.strip('/'))
        self._log('DEBUG', 'Output path for {} is {}'.format(file_in, file_out))
        return file_out

    def _log(self, level, message):
        """
        Helper method to log events.
        Uses the logger provided on initialization to add logs.
        """
        self.logger.log(message=message, level=level, tag=self.tag)
