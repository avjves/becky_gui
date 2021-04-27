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
Here are "global" tests for each Provider.
These tests don't at all look at how the data is saved etc.
They merely test that each provider can backup the data and restore it.

Each provider should implement their own tests that set up the selected
provider properly (create folders, add settings etc.) and then call the
actual test function to run the tests. These tests are completely
provider agnostic. They merely run a backup, restore specific data and asserts
that those files can be found in the restore folder.
"""

class ProviderTests(TestCase):
    def setUp(self):
        GlobalParameter.save_parameter('fs_root', '/')

    def tearDown(self):
        pass

    def test_local_provider_single_folder(self):
        backup_model = Backup(name='_test_backup', provider='local', running=0, status='')
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self._test_backup_model_single_folder(backup_model)
        backup_folder.cleanup()
        
    def test_local_provider_single_file(self):
        backup_model = Backup(name='_test_backup', provider='local', running=0, status='')
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self._test_backup_model_single_file(backup_model)
        backup_folder.cleanup()



##############################################################
# Abstract tests that should be completely provider agnostic #
##############################################################
        
    def _test_backup_model_single_file(self, backup_model):
        test_directory = TemporaryDirectory()
        for i in range(0, 5):
            restore_directory = TemporaryDirectory()
            create_test_files(test_directory.name, 50)
            generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
            files = [f for f in generated_files if not os.path.isdir(f)]
            file_to_backup = random.choice(files)
            backup_model.add_backup_file(test_directory.name)
            backup_model.run_backup()
            backup_model.restore_files([file_to_backup], restore_directory.name)
            files_to_backup = path_to_folders(file_to_backup)
            restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
            restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
            self.assertSetEqual(set(files_to_backup), set(restored_files), fail_message)
            restore_directory.cleanup()
        test_directory.cleanup()

    def _test_backup_model_single_folder(self, backup_model):
        test_directory = TemporaryDirectory()
        for i in range(0, 5):
            restore_directory = TemporaryDirectory()
            create_test_files(test_directory.name, 50)
            generated_files = glob.glob(test_directory.name + '/**/*', recursive=True)
            folders = [f for f in generated_files if os.path.isdir(f)]
            folder_to_restore = random.choice(folders)
            backup_model.add_backup_file(test_directory.name)
            backup_model.run_backup()
            backup_model.restore_files([folder_to_restore], restore_directory.name)
            files_to_be_restored = glob.glob(folder_to_restore + '/**/*', recursive=True)
            files_to_be_restored += path_to_folders(folder_to_restore)
            restored_files = glob.glob(restore_directory.name + '/**/*', recursive=True)
            restored_files = [remove_prefix(f, restore_directory.name) for f in restored_files]
            restored_files.insert(0, folder_to_restore)
            self.assertSetEqual(set(files_to_be_restored), set(restored_files), fail_message)
            restore_directory.cleanup()
        test_directory.cleanup()