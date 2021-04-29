import uuid
import os
import random
import glob
from tempfile import TemporaryDirectory

from django.test import TestCase
from backups.models import Backup
from becky.utils import path_to_folders


class LocalScannerTests(TestCase):
    def setUp(self):
        self.backup_model = Backup(name='_test_backup', provider='', running=0)
        self.backup_model.save()
        self.backup_model.add_parameter('fs_root', '/')
        self.scanner = self.backup_model.get_file_scanner()
        self.database = self.backup_model.get_state_database()
        self.database.clear(self.scanner.tag)
        self.test_directory =  TemporaryDirectory()
        self._create_test_files()

    def tearDown(self):
        self.test_directory.cleanup()
        self.database.clear(self.scanner.tag)



    def _create_test_files(self):
        random_files = [str(uuid.uuid4()) for i in range(0, 50)]
        cur_f = self.test_directory.name
        for random_file in random_files:
            is_dir = random.randint(0, 5)
            if is_dir:
                cur_f = os.path.join(cur_f, random_file)
                os.mkdir(cur_f)
            else:
                open(os.path.join(cur_f, random_file), 'w').write('rnd')


    def test_initial_file_scanning(self):
        """
        Tests backing up a whole folder for the first time.
        Uses glob to find all files from a given folder (given folder is part of these files).
        Asserts that these files are the same as the new files the LocalScanner finds.
        """
        all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files += path_to_folders(self.test_directory.name)
        initial_backup_file = self.backup_model.create_backup_file_instance(self.test_directory.name)
        self.scanner.scan_files([initial_backup_file])
        files = self.scanner.get_changed_files()
        paths = [f.path for f in files]
        self.assertSetEqual(set(all_files), set(paths))

    def test_new_files_added(self):
        """
        After running through a full scanning, adds more files to the directory and asserts
        that a second file scanning finds the newly added files.
        """
        all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files += path_to_folders(self.test_directory.name)
        initial_backup_file = self.backup_model.create_backup_file_instance(self.test_directory.name)
        self.scanner.scan_files([initial_backup_file])
        self._create_test_files()
        new_all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        just_new_files = set(new_all_files).difference(set(all_files))
        self.scanner.mark_new_files()
        self.scanner.scan_files([initial_backup_file])
        files = self.scanner.get_changed_files()
        paths = [f.path for f in files]
        self.assertSetEqual(set(just_new_files), set(paths))

    def test_mark_initial_files(self):
        """
        Tests that the state of files in the state database is accurate
        after marking initial files.
        """
        all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files += path_to_folders(self.test_directory.name)
        initial_backup_file = self.backup_model.create_backup_file_instance(self.test_directory.name)
        self.scanner.scan_files([initial_backup_file])
        self.scanner.mark_new_files()
        new_files = [new_file.path for new_file in self.database.get(self.scanner.tag, 'new_files', [])]
        backed_up_files = [backed_up_file.path for backed_up_file in self.database.get(self.scanner.tag, 'backed_up_files', [])]
        self.assertEqual(new_files, [])
        self.assertSetEqual(set(backed_up_files), set(all_files))


    def test_mark_new_files(self):
        """
        Tests that the state of files in the state database is accurate
        after marking new files.
        """
        all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files += path_to_folders(self.test_directory.name)
        initial_backup_file = self.backup_model.create_backup_file_instance(self.test_directory.name)
        self.scanner.scan_files([initial_backup_file])
        self.scanner.mark_new_files()
        self._create_test_files()
        new_all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files = all_files + new_all_files
        self.scanner.scan_files([initial_backup_file])
        self.scanner.mark_new_files()
        new_files = [new_file.path for new_file in self.database.get(self.scanner.tag, 'new_files', [])]
        backed_up_files = [backed_up_file.path for backed_up_file in self.database.get(self.scanner.tag, 'backed_up_files', [])]
        self.assertEqual(new_files, [])
        self.assertSetEqual(set(backed_up_files), set(all_files))


    def test_files_deleted(self):
        """
        After running through a full scanning, deletes some files from the directory.
        A second scan should not find anything new - delete is not a observed change.
        """
        all_files = glob.glob(self.test_directory.name + '/**/*', recursive=True)
        all_files += path_to_folders(self.test_directory.name)
        all_files.sort(key=len, reverse=True)
        initial_backup_file = self.backup_model.create_backup_file_instance(self.test_directory.name)
        self.scanner.scan_files([initial_backup_file])
        self.scanner.mark_new_files()
        for i in range(0, 10):
            os.system("rm -rf {}".format(all_files[i]))


