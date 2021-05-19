import glob
import json
import os
import random
import time
from tempfile import TemporaryDirectory

from django.test import TestCase

from backups.models import Backup
from becky.utils import join_file_path

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


        
    def test_backup_model_single_file_different_version(self):
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

        for i in range(4, -1, -1): #Trying to restore the file in reverse order.
            restore_directory = TemporaryDirectory()
            timestamp = backup_infos[i]['timestamp']
            restored_files = self.backup_model.restore_files([test_file_path], restore_directory.name, timestamp=timestamp)
            restored_data = open(join_file_path(restore_directory.name, test_file_path), "r").read()
            restore_directory.cleanup()
            self.assertTrue(restored_data == str(i), 'Wrong file restored at iteration {}'.format(i))


