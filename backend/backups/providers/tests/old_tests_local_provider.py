import uuid
import os
import random
import glob
import json
from tempfile import TemporaryDirectory

from django.test import TestCase
from backups.models import Backup
from becky.utils import create_test_files, remove_prefix, path_to_folders

class LocalProviderTests(TestCase):
    def setUp(self):
        self.backup_model = Backup(name='_test_backup', provider='local', running=0)
        self.backup_model.save()
        self.backup_model.add_parameter('fs_root', '/')
        self.scanner = self.backup_model.get_file_scanner()
        self.database = self.backup_model.get_state_database()
        self.provider = self.backup_model.get_backup_provider()
        self.database.clear(self.scanner.tag)
        self.database.clear(self.provider.tag)
        self.test_directory =  TemporaryDirectory()
        self.backup_directory = TemporaryDirectory()
        self.restore_directory = TemporaryDirectory()
        self.backup_model.add_backup_file(self.test_directory.name)
        provider_settings = {'output_path': self.backup_directory.name, 'restore_path': self.restore_directory.name}
        self.backup_model.add_parameter('providerSettings', json.dumps(provider_settings))
        create_test_files(self.test_directory.name, 50)

    def tearDown(self):
        self.test_directory.cleanup()
        self.backup_directory.cleanup()
        self.restore_directory.cleanup()
        self.database.clear(self.scanner.tag)
        self.database.clear(self.provider.tag)

    def test_backup_intial_files(self):
        """
        Tests that on initial backup all files are properly backed up
        to the backup folder.
        """
        files_to_copy = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        files_to_copy += path_to_folders(self.test_directory.name)
        self.backup_model.run_backup()
        copied_files = glob.glob(self.backup_directory.name + '/**/*', recursive=True)
        copied_files = [remove_prefix(f, self.backup_directory.name) for f in copied_files]
        self.assertSetEqual(set(files_to_copy), set(copied_files))

    def test_backup_new_files(self):
        """
        Tests that new files added after the initial backup process
        are properly backed up on subsequent runs.
        """
        self.backup_model.run_backup()
        create_test_files(self.test_directory.name, 25)
        files_to_copy = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        files_to_copy += path_to_folders(self.test_directory.name)
        self.backup_model.run_backup()
        copied_files = glob.glob(self.backup_directory.name + '/**/*', recursive=True)
        copied_files = [remove_prefix(f, self.backup_directory.name) for f in copied_files]
        self.assertSetEqual(set(files_to_copy), set(copied_files))

    def test_intial_remote_files_database_state(self):
        """
        Tests that the local database state of remote files is in sync
        after initial backup.
        """
        self.backup_model.run_backup()
        copied_files = glob.glob(self.backup_directory.name + '/**/*', recursive=True)
        copied_files = [remove_prefix(f, self.backup_directory.name) for f in copied_files]
        remote_files = self.database.get(self.provider.tag, 'remote_files')
        remote_files = [f.path for f in remote_files]
        self.assertSetEqual(set(copied_files), set(remote_files))

    def test_new_remote_files_database_state(self):
        """
        Tests that the local database state of remote files is in sync
        after subsequent backups.
        """
        self.backup_model.run_backup()
        create_test_files(self.test_directory.name, 25)
        self.backup_model.run_backup()
        copied_files = glob.glob(self.backup_directory.name + '/**/*', recursive=True)
        copied_files = [remove_prefix(f, self.backup_directory.name) for f in copied_files]
        remote_files = self.database.get(self.provider.tag, 'remote_files')
        remote_files = [f.path for f in remote_files]
        self.assertSetEqual(set(copied_files), set(remote_files))


    def test_get_remote_files_at_path(self):
        """
        Test that the get_remote_files function returns the proper files
        given a path.
        E.g. /home/projects should return all backed up files that are on that
        folder.
        """
        self.backup_model.run_backup()
        files_at_root = os.listdir(self.backup_directory.name + '/')
        backed_up_at_root = self.provider.get_remote_files('/')
        self.assertSetEqual(set(files_at_root), set(backed_up_at_root))
        folders_at_root = [f for f in files_at_root if os.path.isdir(os.path.join(self.backup_directory.name, f))]
        files_at_folder = os.listdir(os.path.join(self.backup_directory.name, folders_at_root[0]))
        backed_up_at_folder = self.provider.get_remote_files('/' + folders_at_root[0])
        self.assertSetEqual(set(files_at_folder), set(backed_up_at_folder))



    def test_restore_file(self):
        """
        Tests that restoring selected files copies the files to the restore 
        path correctly.
        """
        self.backup_model.run_backup()
        backed_up_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        files = [f for f in backed_up_files if not os.path.isdir(f)]
        selected_files = files[0:5]
        self.backup_model.restore_files(selected_files, self.restore_directory.name)
        restored_files = glob.glob(self.restore_directory.name + '/**/*', recursive=True)
        for f in selected_files:
            file_name = f.split('/')[-1]
            found = False
            for restored_file in restored_files:
                if restored_file.endswith(file_name):
                    found = True
                    break
            self.assertTrue(found, 'File {} not restored!'.format(f))
        
    




