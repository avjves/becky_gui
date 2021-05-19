import json
from tempfile import TemporaryDirectory
from django.test import TestCase
from backups.models import Backup
import backups.providers.tests.generic_tests as generic_tests

class LocalProviderTests(TestCase):
    def setUp(self):
        self.generic_tests = generic_tests.GenericTests()
        pass

    def tearDown(self):
        pass

    def test_single_folder(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_folder(backup_model)
        backup_folder.cleanup()
        
    def test_single_file(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_file(backup_model)
        backup_folder.cleanup()

    def test_single_differential_file(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_differential_file(backup_model)
        backup_folder.cleanup()

    def test_single_differential_file_wrong_timestamp(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_differential_file_wrong_timestamp(backup_model)
        backup_folder.cleanup()


    def test_verify_files(self):
        backup_model = Backup(name='_test_backup', provider='local+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        provider_settings = json.dumps({'output_path': backup_folder.name})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_file_verification(backup_model)
        backup_folder.cleanup()


