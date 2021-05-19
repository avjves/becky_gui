import glob
import json
import os
import random
from tempfile import TemporaryDirectory

from django.test import TestCase

from backups.models import Backup
from becky.utils import create_test_files, remove_prefix, path_to_folders
from settings.models import GlobalParameter


"""
Here are "global" tests that each Provider should call in their own tests.
These tests don't at all look at how the data is saved/scanned etc.
They merely test that each provider can backup the data and restore it.

Each provider should implement their own tests that set up the selected
provider properly (create folders, add settings etc.) and then call the
actual test function to run the tests. These tests are completely
provider agnostic. 
"""

class AgnosticTests(TestCase):

    def _test_backup_model_single_file(self, backup_model):
        """
        Tests backing up random files and restoring a single file from the backup.
        Restores both the file in question as well as all the folders that take 
        to the specific file.
        Makes sure only the correct file/folders are in the restore folder and that the
        file is actually a file.
        """
        test_directory = TemporaryDirectory()
        files = set()
        for i in range(0, 5):
            restore_directory = TemporaryDirectory()
            create_test_files(test_directory.name, 50)
            generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
            new_files = [f for f in generated_files if not os.path.isdir(f) and f not in files]
            file_to_backup = random.choice(new_files)
            files = files.union(set(new_files))
            backup_model.add_backup_file(test_directory.name)
            backup_info = backup_model.run_backup()
            restored_files = backup_model.restore_files([file_to_backup], restore_directory.name, timestamp=backup_info['timestamp'])
            files_to_backup = path_to_folders(file_to_backup)
            restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
            restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
            self.assertFalse(os.path.isdir(restored_files[-1])) # Last file has to be a file, not a folder!
            self.assertSetEqual(set(files_to_backup), set(restored_files))
            restore_directory.cleanup()
        test_directory.cleanup()

    def _test_backup_model_single_differential_file(self, backup_model):
        """
        Tests backing up random files multiple times differentially and afterwards 
        restoring a file from multiple timestamps.
        Restores both the file in question as well as all the folders that take 
        to the specific file.
        Makes sure only the correct file/folders are in the restore folder and that the
        file is actually a file.
        """
        test_directory = TemporaryDirectory()
        restore_directory = TemporaryDirectory()
        create_test_files(test_directory.name, 50)
        generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
        files = [f for f in generated_files if not os.path.isdir(f)]
        file_to_backup = random.choice(files)
        backup_model.add_backup_file(test_directory.name)
        first_backup_info = backup_model.run_backup()
        create_test_files(test_directory.name, 50)
        second_backup_info = backup_model.run_backup()
        backup_model.restore_files([file_to_backup], restore_directory.name, timestamp=first_backup_info['timestamp'])
        files_to_backup = path_to_folders(file_to_backup)
        restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
        restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
        self.assertFalse(os.path.isdir(restored_files[-1])) # Last file has to be a file, not a folder!
        self.assertSetEqual(set(files_to_backup), set(restored_files))
        restore_directory.cleanup()
        test_directory.cleanup()

    def _test_backup_model_single_differential_file_wrong_timestamp(self, backup_model):
        """
        Tests backing up multiple files differentially and then intetionally
        attempting to restore a file with the wrong timestamp.
        This should fail.
        """
        test_directory = TemporaryDirectory()
        restore_directory = TemporaryDirectory()
        create_test_files(test_directory.name, 50)
        generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
        files = set([f for f in generated_files if not os.path.isdir(f)])
        backup_model.add_backup_file(test_directory.name)
        first_backup_info = backup_model.run_backup()
        create_test_files(test_directory.name, 50)
        generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
        new_files = [f for f in generated_files if not os.path.isdir(f) and f not in files]
        file_to_backup = random.choice(new_files)
        second_backup_info = backup_model.run_backup()
        backup_model.restore_files([file_to_backup], restore_directory.name, timestamp=first_backup_info['timestamp'])
        files_to_backup = path_to_folders(file_to_backup)
        restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
        restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
        self.assertSetEqual(set(), set(restored_files))
        restore_directory.cleanup()
        test_directory.cleanup()



    def _test_backup_model_single_folder(self, backup_model):
        """
        Tests backing up random files/folders and restoring a single folder from the backup.
        Restores all folders that build up to the folder in question as well as all files
        and folders inside the specific folder.
        Makes sure that only the necessary files are restored and that their file formats
        are set correctly.
        """
        test_directory = TemporaryDirectory()
        new_files = set()
        for i in range(0, 5):
            restore_directory = TemporaryDirectory()
            create_test_files(test_directory.name, 50)
            generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
            new_folders = [f for f in generated_files if os.path.isdir(f) if f not in new_files]
            folder_to_restore = random.choice(new_folders)
            new_files = new_files.union(set(new_folders))
            backup_model.add_backup_file(test_directory.name)
            backup_info = backup_model.run_backup()
            restored_files = backup_model.restore_files([folder_to_restore], restore_directory.name, timestamp=backup_info['timestamp'])
            files_to_be_restored = glob.glob(folder_to_restore + '/**/*', recursive=True)
            files_to_be_restored = [f for f in files_to_be_restored if not os.path.isdir(f)]
            restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
            restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
            restored_files = [f for f in restored_files if not os.path.isdir(f)]
            self.assertSetEqual(set(files_to_be_restored), set(restored_files), 'Missing files on iteration {}.'.format(i))
            for f in files_to_be_restored:
                backup_file_type = 'folder' if os.path.isdir(f) else 'file'
                restored_file_type = 'folder' if os.path.isdir(restore_directory.name + f) else 'file'
                self.assertTrue(backup_file_type == restored_file_type, 'File type mismatch on iteration {}.'.format(i))
            restore_directory.cleanup()
        test_directory.cleanup()

    def _test_backup_model_file_verification(self, backup_model):
        """
        Tests backing up random files and then verifying that the checksums match.
        """
        test_directory = TemporaryDirectory()
        create_test_files(test_directory.name, 50)
        generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
        backup_model.add_backup_file(test_directory.name)
        backup_model.run_backup()
        verified = backup_model.verify_files()
        self.assertTrue(verified)
        test_directory.cleanup()

    
    def _test_backup_model_single_file_different_version(self, backup_model):
        """
        Tests backing up a random file, changing it and then backing it up again.
        Ensures that restoring the file with the correct timestamp results in
        the correct version of the file to be restored.
        """
        test_directory = TemporaryDirectory()
        os.makedirs(os.path.join(test_directory.name, 'folder'))
        test_file_path = os.path.join(test_directory.name, 'folder', 'file')
        backup_model.add_backup_file(test_directory.name)
        backup_infos = []

        for i in range(0, 5): # Saving files
            open(test_file_path, "w").write(str(i))
            backup_info = backup_model.run_backup()
            backup_infos.append(backup_info)

        for i in range(4, -1, -1): #Trying to restore the file in reverse order.
            restore_directory = TemporaryDirectory()
            timestamp = backup_infos['timestamp']
            restored_files = backup_model.restore_files([test_file_path], restore_directory.name, timestamp=timestamp)
            print(restored_files)
            self.assertTrue(False)


