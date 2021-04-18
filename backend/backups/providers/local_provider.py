import os
from shutil import copyfile
from backups.providers.base_provider import BaseProvider

"""
A local backup provider that can backup files from one location
to another, within a local system.
"""
class LocalBackupProvider(BaseProvider):
    
    def __init__(self, parameters, logger, backup_model):
        self.parameters = parameters
        self.logger = logger
        self.backup_model = backup_model
        self.tag = 'LocalBackupProvider'

    def backup_files(self, list_of_files):
        """
        Receives a list of files to be backed up. 
        TODO: Use rsync or something a bit more efficient than
        going through files one at a time.
        """
        self._log('INFO', 'Started backing up files.')
        list_of_files.sort() # Sort, so folders will be created before any files are copied in.
        # self.starting_path = parameters['path']
        starting_path = '/home/avjves/projects'
        # self.copy_path = parameters['copy_path']
        copy_path = '/home/avjves/copy_test'
        self._log('INFO', 'Files sorted, starting backing up {} files.'.format(len(list_of_files)))
        for file_in_index, file_in in enumerate(list_of_files):
            file_out = self._generate_output_path(file_in, starting_path, copy_path)
            self._copy_file(file_in, file_out)
            if file_in_index % 1000 == 0:
                self._log('DEBUG', '{} new files backed up.'.format(file_in_index))
        self._log('INFO', '{} new files backed up.'.format(len(list_of_files)))

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

    def _generate_output_path(self, file_in, starting_path, copy_path):
        """
        Strips unnecessary suffix from the file_in parameter using the starting path and 
        generates an output path for the file.
        """
        file_out = file_in[len(starting_path):] #Remove the 'suffix'
        file_out = '{}{}'.format(copy_path, file_out)
        return file_out

    def _log(self, level, message):
        """
        Helper method to log events.
        Uses the logger provided on initialization to add logs.
        """
        self.logger.log(message=message, level=level, tag=self.tag)
