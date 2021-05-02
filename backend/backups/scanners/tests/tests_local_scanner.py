import os
from tempfile import TemporaryDirectory
from django.test import TestCase

from backups.models import Backup
from becky.utils import path_to_folders, join_file_path

class LocalScannerTests(TestCase):

    def setUp(self):
        self.backup_model = Backup(name='_test_backup', provider='', scanner='local', running=0)
        self.backup_model.save()
        self.scanner = self.backup_model.get_file_scanner()
        pass

    def tearDown(self):
        pass


    def test_scan_hidden_files(self):
        """
        Makes sure the scanner can find hidden files and hiden folders.
        Creates a temporary directory with some hidden files
        """
        folder_to_scan = TemporaryDirectory()
        hidden_folder = os.path.join(folder_to_scan.name, '.hidden_folder')
        hidden_files = [
            join_file_path(folder_to_scan.name, 'normal_file'),
            join_file_path(folder_to_scan.name, '.hidden_file'),
            join_file_path(folder_to_scan.name, '.hidden_folder', 'normal_file'),
            join_file_path(folder_to_scan.name, '.hidden_folder', '.hidden_file'),
        ]
        os.mkdir(hidden_folder)
        open(hidden_files[0], "w").write('normal_data')
        open(hidden_files[1], "w").write('hidden_data')
        open(hidden_files[2], "w").write('normal_data inside hidden folder')
        open(hidden_files[3], "w").write('hidden_data inside hidden folder')
        backup_file = self.backup_model.add_backup_file(folder_to_scan.name)
        found_files = self.scanner.scan_files([backup_file])
        found_files_paths = [f.path for f in found_files]
        self.assertSetEqual(set(found_files_paths), set(hidden_files + [hidden_folder] + path_to_folders(folder_to_scan.name)))
        
