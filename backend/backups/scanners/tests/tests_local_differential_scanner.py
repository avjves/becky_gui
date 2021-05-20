import os
import json
import time
from tempfile import TemporaryDirectory
from django.test import TestCase
from django.utils import timezone

from backups.models import Backup
from becky.utils import path_to_folders, join_file_path

class LocalDifferentialScannerTests(TestCase):

    def setUp(self):
        self.backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        self.backup_model.save()
        self.scanner = self.backup_model.get_file_scanner()
        self.backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': self.backup_folder.name})
        self.backup_model.add_parameter('providerSettings', provider_settings)

    def tearDown(self):
        self.backup_folder.cleanup()


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
        current_timestamp = timezone.now()
        backup_file = self.backup_model.add_backup_file(folder_to_scan.name)
        found_files = self.scanner.scan_files([backup_file], current_timestamp)
        found_files_paths = [f.path for f in found_files]
        self.assertSetEqual(set(found_files_paths), set(path_to_folders(hidden_folder) + hidden_files))
        

    def test_scan_differential_files(self):
        """
        Makes sure the scanner flags files that are changed (NOT created) after the initial scan.
        """
        folder_to_scan = TemporaryDirectory()
        folder = os.path.join(folder_to_scan.name, 'folder')
        files = [
            join_file_path(folder_to_scan.name, 'folder', 'normal_file'),
            join_file_path(folder_to_scan.name, 'folder', 'static_file'),
        ]
        os.mkdir(folder)
        open(files[0], "w").write('normal_data')
        open(files[1], "w").write('static_data')
        backup_file = self.backup_model.add_backup_file(folder_to_scan.name)
        backup_info = self.backup_model.run_backup() #Running a full scan, which should backup all the initial files
        time.sleep(2)
        open(files[0], "w").write('normal_data_changed')
        current_timestamp = timezone.now()
        found_files = self.scanner.scan_files([backup_file], current_timestamp) #Now we don't really need to fully run backup, so just calling the scanner directly here to test this specific functionality
        found_files_paths = [f.path for f in found_files]
        self.assertSetEqual(set(found_files_paths), set([files[0]])) #On second iteration the found files should JUST be the changed file

