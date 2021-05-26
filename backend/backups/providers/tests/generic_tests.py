import glob
import json
import os
import random
import time
import shutil
from tempfile import TemporaryDirectory

from django.test import TestCase

from backups.models import Backup
from becky.utils import join_file_path, create_test_files

"""
Here are generic tests, that, at least for now, don't have to be called by
each provider. Here we just use a local provider to test this functionality.
Therefore these are more generic tests that just make sure the logic works around
the provider without testing any provider specific implementations. Those tests
should be tested on their own corresponding test files.
"""

class GenericTests(TestCase):

    def setUp(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=1)
        backup_model.save()
        self.backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': self.backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.backup_model = backup_model

    def tearDown(self):
        self.backup_folder.cleanup()


        
    def test_restore_single_file_different_version(self):
        """
        Tests backing up a random file, changing it and then backing it up again.
        Ensures that restoring the file with the correct timestamp results in
        the correct version of the file to be restored.
        """
        test_directory = TemporaryDirectory()
        os.makedirs(os.path.join(test_directory.name, 'folder'))
        test_file_path = os.path.join(test_directory.name, 'folder', 'file')
        self.backup_model.add_backup_file(test_directory.name)
        backup_infos = []

        for i in range(0, 5): # Saving files
            open(test_file_path, "w").write(str(i))
            backup_info = self.backup_model.run_backup()
            backup_infos.append(backup_info)
            time.sleep(1)

        for i in range(0, 5): 
            restore_directory = TemporaryDirectory()
            timestamp = backup_infos[i]['timestamp']
            restored_files = self.backup_model.restore_files([test_file_path], restore_directory.name, timestamp=timestamp)
            restored_data = open(join_file_path(restore_directory.name, test_file_path), "r").read()
            restore_directory.cleanup()
            self.assertTrue(restored_data == str(i), 'Wrong file restored at iteration {}'.format(i))


    def test_get_remote_files_at_path(self):
        """
        Tests the function called by views (called by the user via the UI) when using the FileTreeViewer.
        The idea is that the user can request all files at, say, /home/user directory and this function
        should return all files and folders at that path. This is completely local, i.e the provider doesn't
        provide this functionality.
        Tests root, the backup folder and a random folder inside the backup folder.
        """
        test_directory = TemporaryDirectory()
        create_test_files(test_directory.name, 50)
        self.backup_model.add_backup_file(test_directory.name)
        backup_info = self.backup_model.run_backup()
        timestamp = backup_info['timestamp']
        remote_files = self.backup_model.get_remote_files('/', timestamp)
        remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
        self.assertSetEqual(set(remote_files), set(), 'Wrong files returned at {}'.format('/'))
        self.assertSetEqual(set(remote_folders), set(['tmp']), 'Wrong folders returned at {}'.format('/'))
        remote_files = self.backup_model.get_remote_files(test_directory.name, timestamp)
        remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
        actual_files = [f for f in os.listdir(test_directory.name) if not os.path.isdir(join_file_path(test_directory.name, f))]
        actual_folders = [f for f in os.listdir(test_directory.name) if os.path.isdir(join_file_path(test_directory.name, f))]
        self.assertSetEqual(set(remote_files), set(actual_files), 'Wrong files returned at {}'.format(test_directory.name))
        self.assertSetEqual(set(remote_folders), set(actual_folders), 'Wrong folders returned at {}'.format(test_directory.name))
        random_folder = random.choice([f for f in glob.glob(test_directory.name + '/**/*', recursive=True) if os.path.isdir(f)])
        remote_files = self.backup_model.get_remote_files(random_folder, timestamp)
        remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
        actual_files = [f for f in os.listdir(random_folder) if not os.path.isdir(join_file_path(random_folder, f))]
        actual_folders = [f for f in os.listdir(random_folder) if os.path.isdir(join_file_path(random_folder, f))]
        self.assertSetEqual(set(remote_files), set(actual_files), 'Wrong files returned at {}'.format(random_folder))
        self.assertSetEqual(set(remote_folders), set(actual_folders), 'Wrong folders returned at {}'.format(random_folder))


    def test_get_remote_files_at_path_at_time(self):
        """
        The same as the 'test_get_remote_files_at_path' test, but tests it on different timestamps. The tested
        function should only return files created at the given timestamp or before, not newer.
        """
        test_directory = TemporaryDirectory()
        helper_folder = os.path.join(test_directory.name, 'helper')
        self.backup_model.add_backup_file(test_directory.name)
        backup_infos = []
        backup_files = []
        os.makedirs(helper_folder)
        for i in range(0, 5):
            create_test_files(helper_folder, 50)
            backup_info = self.backup_model.run_backup()
            backup_infos.append(backup_info)
            files = glob.glob(test_directory.name + '/**/*', recursive=True)
            folders = [f for f in files if os.path.isdir(f)] # Add previous iteration folders to current iteration
            files = [f for f in files if not os.path.isdir(f)] # same with files
            backup_files.append([files, folders])

        for i in range(0, 5):
            timestamp = backup_infos[i]['timestamp']
            remote_files = self.backup_model.get_remote_files('/', timestamp)
            remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
            self.assertSetEqual(set(remote_files), set(), 'Wrong files returned at {} on iteration {}'.format('/', i))
            self.assertSetEqual(set(remote_folders), set(['tmp']), 'Wrong folders returned at {} on iteration {}'.format('/', i))
            remote_files = self.backup_model.get_remote_files(test_directory.name + '/helper', timestamp)
            remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
            actual_files = [f.split('/')[-1] for f in backup_files[i][0] if f.rsplit('/', 1)[0].endswith('/helper')]
            actual_folders = [f.split('/')[-1] for f in backup_files[i][1] if f.rsplit('/', 1)[0].endswith('/helper')]
            self.assertSetEqual(set(remote_files), set(actual_files), 'Wrong files returned at {} on iteration {}'.format(test_directory.name + '/helper', i))
            self.assertSetEqual(set(remote_folders), set(actual_folders), 'Wrong folders returned at {} on iteration {}'.format(test_directory.name + '/helper', i))
            random_folder = random.choice(backup_files[i][1])
            remote_files = self.backup_model.get_remote_files(random_folder, timestamp)
            remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
            actual_files = [f.split('/')[-1] for f in backup_files[i][0] if f.rsplit('/', 1)[0].endswith(random_folder)]
            actual_folders = [f.split('/')[-1] for f in backup_files[i][1] if f.rsplit('/', 1)[0].endswith(random_folder)]
            self.assertSetEqual(set(remote_files), set(actual_files), 'Wrong files returned at {} on iteration {}'.format(random_folder, i))
            self.assertSetEqual(set(remote_folders), set(actual_folders), 'Wrong folders returned at {} on iteration {}'.format(random_folder, i))
        test_directory.cleanup()

    def test_get_remote_file_type_change(self):
        """
        Tests backing up a file, then deleting it and creating a same named folder (+ file inside it) and backups it.
        This is here to test that the get_remote_file properly returns both a file and a folder version when necessary.
        """
        test_directory = TemporaryDirectory()
        test_path = os.path.join(test_directory.name, 'test')
        test_f_path = os.path.join(test_path, 'tf')
        self.backup_model.add_backup_file(test_directory.name)
        open(test_path, 'w').write('test')
        first_backup_info = self.backup_model.run_backup()
        time.sleep(1)
        os.remove(test_path)
        os.makedirs(test_path)
        open(test_f_path, "w").write('test')
        second_backup_info = self.backup_model.run_backup()
        remote_files = self.backup_model.get_remote_files(test_directory.name, first_backup_info['timestamp'])
        remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
        self.assertListEqual(remote_files, ['test'], "Files don't match!")
        self.assertListEqual(remote_folders, [], "Folders don't match!")
        remote_files = self.backup_model.get_remote_files(test_directory.name, second_backup_info['timestamp'])
        remote_files, remote_folders = [f.filename for f in remote_files if f.file_type == 'file'], [f.filename for f in remote_files if f.file_type == 'directory']
        self.assertListEqual(remote_files, [], "Files don't match!")
        self.assertListEqual(remote_folders, ['test'], "Folders don't match!")
